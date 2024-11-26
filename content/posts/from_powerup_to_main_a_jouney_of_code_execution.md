---
title: 'From Power Up to Main: The Journey of Code Execution'
date: 2024-11-05T12:02:28+01:00
draft: false
cover:
    image: from_boot_to_main/cover1
---

#### Assumptions
I'm assuming you have some basic knowledge of the compilation process and a little about linkers,
you don't need to be an expert

### Why Understanding Matters
I'm not a big fan of the idea that I can just press the green button and, boom, my code is somehow
executing and being debugged on my MCU. I always like to understand what happens before I start using
that IDE. In this article, you'll learn what goes on under the hood, and this knowledge can help you
become independent from any IDE but also enable you to add custom frimware maybe your OS...

#### Case Study: STM43F446RE
I'm going to use the STM32F446RE as a demonstration, but the process is very similar, especially
for other Cortex-M microcontrollers.

#### BOOT Process
Let's answer the question of how this MCU boots. for example, if you are familiar with x86 architecture,
you might know that there's special location where the cpu "starts", such as the MBR, and that there are
operating modes like real mode and protected mode. if you're not familiar with this. don't worry, I'll
explain.
![](/from_boot_to_main/ds_boot_modes.png)

Wait, What are 'BOOT pins'? Well, typically, MCU manufactures provide jumpers that allow you to configure
the boot options. This configuration is usually done using jumpers that look like these.
![](/from_boot_to_main/330px-Jumper_on_motherboard.jpg)
let's see if my MCU has them
![](/from_boot_to_main/boot_pins_pic1.png)
**That’s still not very clear. Now I have Three questions:**
1. How many pins should there be?
2. Which values correspond to each mode?
3. Most importantly, where are these pins located on the MCU so I can configure them? Or, if they’re hardwired, how can I determine which mode is set?

**Answers**
1. Since there are three modes, there should be at least two pins.
2. here's encoding of each mode
![](/from_boot_to_main/rf_boot_configuration.png)

I had a question about SYSCLK: Do I need to set something to select which oscillator to use?
Well, as you can see, we don't need to worry about it.
![](/from_boot_to_main/sysclk1.png)
![](/from_boot_to_main/sysclk2.png)

3. here's default value of BOOT0
![](/from_boot_to_main/boot1_p.png)
![](/from_boot_to_main/boot2_p.png)
![](/from_boot_to_main/boot3_p.png)

With this knowledge, we understand that we are booting from flash memory.

**So What?**
well first my code should be in flash, later we'll look into the memory map for more info

#### RESET
![](/from_boot_to_main/pm_on_reset1.png)
![](/from_boot_to_main/pm_on_reset2.png)
![](/from_boot_to_main/rf_on_reset1.png)
![](/from_boot_to_main/cpu_at.gif)

If you've noticed, the term 'reset vector' appears frequently, which might suggest a connection to
something called the vector table. Let's take a closer look at it.
![](/from_boot_to_main/vector_table.png)

#### What We Know So Far
- booting from flash
- At reset, the MCU loads the stack pointer (sp) from address 0x00000004 and sets the program counter (pc) to the *reset vector*, which is located at 0x00000004
- vector table is located at 0x00000000

#### Memory Map
I usually like to look at the memory map to get a sense of where everything is located.
it really helps me when debugging at this level
![](/from_boot_to_main/memory_map.png)

As you can see, flash memory is located at 0x08000000, so when constructing the ELF file, the vector
table with the correct values should be placed there.

This is rough explanation at this point.
![](/from_boot_to_main/rough_idea_at_reset.png)

I'll blink the LED, but what matters is not what's inside the 'main' function. I'm explaining how we
reached that point.

Okay, now let's place the vector table at the start. Usually, when I need this level of control over
where certain things should go, I create custom sections. This way, I can reference them later in the linker script.

By the way, I'm using the GNU toolchain, and here's how you do it
![](/from_boot_to_main/custom_sections1.png)
![](/from_boot_to_main/custom_sections2.png)

so let's construct vector table, According to
![](/from_boot_to_main/vector_table_entries.png)

here's what the [source](https://github.com/Gharbaoui/from_power_up_to_main/blob/411b36d52b3d068e9289bd2849ce0b060111af62/startup.c)

focus only on these for now
```c
uint32_t vector_table[] __attribute__((section (".cs_vectors"))) = {
  (uint32_t)&_start_of_sram,
  (uint32_t)reset_vector,
  ...
}
```

You might have questions about the other 'attribute'—let me explain. Since I’m not focusing on other
interrupts for now, I won’t implement them. Some of them are user-defined, so instead of implementing
all of them, we’ll use
```c
__attribute__((weak, alias("blocking_handler")))
```

to say that if this symbol is not defined, it will default to "blocking_handler", here's small demonstration:

```c
// test.c file
int default_add(int a, int b) {return a + b;}

int add(int, int) __attribute__((weak, alias("default_add")));

int main()
{
    return add(3, 2);
}

// add.c file
int add(int a, int b) {
  return a + b + 34;
}
```

![](/from_boot_to_main/weak_alias_demo1.png)
![](/from_boot_to_main/weak_alias_demo2.png)

and if you have question about "_start_of_sram" that will come from linker script and if you have
been following this far, you would know whatever the value of this "_start_of_sram", will be stored
in stack pointer so it should be at the end of sram since the stack is going "down"

let's write a simple linker script [look at](https://github.com/Gharbaoui/from_power_up_to_main/blob/42d723d49a15075c63fb2afe9f75e6768ab87f8f/linker_script.ld)
![](/from_boot_to_main/linker_sc_1.png)
![](/from_boot_to_main/linker_sc_2.png)

```ld
PROVIDE(_start_of_sram = ORIGIN(sram) + LENGTH(sram));
```
This is the point where '_start_of_sram' is set. Now, keep a close eye on this.

```ld
> sram AT > flash
```
What we’re saying here is that the virtual address will be in SRAM, while the logical address will be in flash.
**But Why?** first of all, the .data section contains initialized global variables.

```c
uint32_t AAA = 90; // it will end up in the .data section
uint32_t b; // in .bss section
int main()
{
    ...
    // something with variable AAA
}
```
So, 'AAA = 90' needs to be stored somewhere persistent, which is why we put it in flash memory since flash
is non-volatile. At startup *(inside reset_vector)*, we'll copy it to SRAM. But why copy it to SRAM? we
could update the value directly in flash, since we can write to flash during frimware updates. However,
writing to flash is expensive in terms of time and resources. Additionally, during the lifetime of your program,
the value will likely change. if we leave it in flash, those changes would be retained across power
cycles, which is not desireable. By copy it to SRAM, we ensure that the value can be modified without affecting
the flash storage, and it will reset to it's default state on the next power-up.
What 'SRAM AT > Flash' means is that when writing the ELF file to the MCU, the .data section will be
placed in flash. However, when referenced in the source code, it will appear as if it is in SRAM.
Remember, in the reset vector, I'll copy the .data section from flash to SRAM before handing control
over to the main function. This way, everything works as expected for the user.

![](/from_boot_to_main/vma_lma_1.png)
![](/from_boot_to_main/vma_lma_1_1.png)

as you can see that assembly of result is referencing SRAM area, and here's if we did just `>flash`
![](/from_boot_to_main/vma_lma_2_2.png)

As you can see, my code would be working directly with flash, which we don't want.
Now, we need to copy the .data section from flash to SRAM and then transfer control to the main function.
To Copy something, we need three things: where to store it, where to read it from, and how much to copy.
Okay let's go back to the linker script

```ld
...
_start_of_text = .;
...
_end_of_text = .;
...
_start_of_data = .;
...
_end_of_data = .;
...
...
```

these are symbols that the linker will add them and we access them from our source files
![](/from_boot_to_main/linker_symbols_provided.png)
![](/from_boot_to_main/startup_copy_sram.png)

Here’s the source code for the copy operation.
```c
extern uint32_t _start_of_text;
extern uint32_t _end_of_text;
extern uint32_t _start_of_data;
extern uint32_t _end_of_data;
extern uint32_t _start_of_bss;
extern uint32_t _end_of_bss;

void reset_vector(void)
{
  const uint32_t data_section_size = &_end_of_data - &_start_of_data;
  uint32_t* data_section_dst_on_sram_ptr = (uint32_t*)&_start_of_data;
  const uint32_t* where_to_start_copy_from_ptr = (uint32_t*)&_end_of_text;

  for (uint32_t i = 0; i < data_section_size; ++i) {
    data_section_dst_on_sram_ptr[i] = where_to_start_copy_from_ptr[i];
  }
}
```

I’m going to do the same for the .bss section.
```c
const uint32_t bss_size = &_end_of_bss - &_start_of_bss;
uint32_t* bss_dst = (uint32_t*)&_start_of_bss;
for (uint32_t i = 0; i < bss_size; ++i)
{
    bss_dst[i] = 0;
}
```

Now we're ready to call "main". By the way, I’ve decided to name it "system_start" instead.

```c
extern void	system_start(void);
void reset_vector(void)
{
  const uint32_t data_section_size = &_end_of_data - &_start_of_data;
  uint32_t* data_section_dst_on_sram_ptr = (uint32_t*)&_start_of_data;
  const uint32_t* where_to_start_copy_from_ptr = (uint32_t*)&_end_of_text;

  for (uint32_t i = 0; i < data_section_size; ++i) {
    data_section_dst_on_sram_ptr[i] = where_to_start_copy_from_ptr[i];
  }

  const uint32_t bss_size = &_end_of_bss - &_start_of_bss;
  uint32_t* bss_dst = (uint32_t*)&_start_of_bss;
  for (uint32_t i = 0; i < bss_size; ++i)
  {
    bss_dst[i] = 0;
  }

  system_start();
}
```

Let’s verify it using gdb. By the way, I’m using Segger J-Link, but you could also use an ST-Link on
board or even GDB with OpenOCD. This is just my preference.

![](/from_boot_to_main/db_1.png)
![](/from_boot_to_main/db_2.png)
![](/from_boot_to_main/db_3.png)

As you can see, it's working. Now, I can put whatever I want there. let's blink the builtin LED.
Here's the source code for it.

```c
#include <stdint.h>
#define GPIOA_ADDR 0x40020000
#define RCC_ADDR 0x40023800

#define RCC_AHB1 *(volatile uint32_t *)(RCC_ADDR + 0x30)
#define GPIOA_ODR *(volatile uint32_t *)(GPIOA_ADDR + 0x14)
#define GPIOA_MODER *(volatile uint32_t *)(GPIOA_ADDR + 0x00)
#define GPIOA_OTYPER *(volatile uint32_t *)(GPIOA_ADDR + 0x04)
#define GPIOA_OSPEEDER *(volatile uint32_t *)(GPIOA_ADDR + 0x08)
#define PIN5_ON (1 << 5)
#define PIN5_OFF ~PIN5_ON

void	system_start(void)
{
	RCC_AHB1 |= 0x01; // enable clock for ahb
	GPIOA_MODER |= (1 << 10); // input or output // bad line
	GPIOA_OSPEEDER |= 0x00; // speed low
	GPIOA_OTYPER |= (0 << 5); // probably will change push-pull drain

	while(1)
	{
		GPIOA_ODR |= PIN5_ON;
		for (int i = 0; i < 500000; ++i);
		GPIOA_ODR &= (PIN5_OFF);
		for (int i = 0; i < 500000; ++i);
	}
}
```
I’m not going to explain this source code right now because this article isn’t about that.
![](/from_boot_to_main/demo.gif)

[source code](https://github.com/Gharbaoui/from_power_up_to_main.git)