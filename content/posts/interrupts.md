---
title: 'Interrupts'
date: 2024-11-23T10:13:09+01:00
draft: true
cover:
    image: interrupts/cover1.webp
---

![](/interrupts/cover.gif)
### Interrupts
- **what are interrupts?**
- **why?**
- **how?**

In short an interrupt is a request for the system to pause what it is currently executing and
temporarily switch to handling something else, often a higher-priority task.

Imagine your software is busy performing a task—perhaps blinking an LED or managing something more complex.
Suddenly, an unexpected event occurs: a button is pressed, a divide-by-zero error arises,
or a PC sensor detects overheating. How do you handle this exceptional scenario? Are you even the one managing it?
One approach is polling, where the software continuously checks for events in a loop—a “super loop.”
While this might work for simple systems, as the number of events grows, this approach becomes inefficient
and quickly overwhelms the system. It may even become impossible to respond to all events in a timely manner.

![](/interrupts/1.gif)

I hope by now you can see the kind of problem interrupts are designed to solve for us.

Now, Let's dive into **HOW**. To be clear, my goal for this part is simple: I want the LED to turn on
when the button is pressed, independently of what else is happening at the moment,
and "what is happening at the moment" I'll do just blink for demonstration
![](/interrupts/2.gif)
As you can see, there’s nothing inside the while loop to check whether the button is pressed or not.

Now, let's get into the details. We'll need to configure the GPIO pins properly to achieve this effect,
where pressing the button will trigger the LED to turn on, independent of the current task.
![](/interrupts/ds_gpio_1.png)

BTW I'm using libopencm3 here's [empty setup](https://github.com/Gharbaoui/libopencm3_empty_setup) if you want to follow

```c
gpio_mode_setup(GPIOB, GPIO_MODE_INPUT, GPIO_PUPD_NONE, GPIO8);
```

Okay, let’s move on to **EXTI**. Usually, I like to understand what’s happening under the hood, so for
a bit, I considered diving into the rabbit hole of implementing my own external interrupt controller.
This part isn’t crucial—it’s just for fun—but after some thought, I decided not to go down that path.
Here’s what I came up with, so feel free to skip ahead to [this](#exti-config)
![](/interrupts/1.png)
#### Wiring
![](/interrupts/assets/1.png)
![](/interrupts/assets/2.jpg)
![](/interrupts/assets/3.jpg)

### How To Run
- make upload_memory

![](/interrupts/assets/5.jpg)
![](/interrupts/assets/4.jpg)
- CH2 (the purple trace) represents your input, connected to the button to simulate changes in the signal.
- CH1 (the yellow trace) displays the output of the edge detector.
- CH3 (the blue trace) shows the clock signal for reference
[source code](https://github.com/Gharbaoui/external_interrupts/tree/main/helpers)

#### EXTI Config
Since I’ve thrown in some concepts that might confuse you, especially regarding FPGAs, and that was
intended for those who want to dive even deeper, here’s what you should keep in mind up to this point
![](/interrupts/2.png)

![](/interrupts/rf_exti_1_1.png)
![](/interrupts/rf_exti_2.png)


From this information, I now understand a few key points:
1. **Flexibility:** We have the option to configure interrupts to trigger on rising edges, falling edges, or both
2. **Masking:** We can specify which lines should generate interrupts. For example, setting `EXTI_IMR[0] = 1` tells **EXTI** to expect interrupts on line 0. (BTW, `IMR[0]` refers to bit 0, not a byte.)

Additionally, we need to inform NVIC to handle interrupts coming from our configured EXTI line (i.e., the output of EXTI).

Wait—what is **NVIC**? That’s a whole different topic! I’ll keep it as minimal as possible in this article
and save the deeper details for another time. Don’t worry—you’ll understand what you need for now,
just not the intricacies of what’s happening under the hood. I’ll tackle those in a future article. For now, let’s keep things simple!

*Masking*
```c
exti_enable_request(EXTI8);
```
![](/interrupts/4.png)

as you can see this is just writing to IMR register nothing fancy

*flexibility*
```c
exti_set_trigger(EXTI8, EXTI_TRIGGER_RISING);
```

But again, we still have no idea how my I/O pin is linked to **EXTI** yet.
![](/interrupts/5.png)
![](/interrupts/6.png)
But with this information, we now understand how GPIO is going to be linked with EXTI.
![](/interrupts/3.gif)
Since I’m going to use EXTI8 and GPIOB, here’s the source code:

```c
exti_select_source(EXTI8, GPIOB);
```
Let’s do a quick sanity check—everything looks fine so far.
![](/interrupts/7.png)
So, all we need to do now is configure the **NVIC**. Looking at the **NVIC** registers, I see:
![](/interrupts/8.png)

But EXTI line 8 is connected to what in the **NVIC**? This is where the vector table comes in. Each interrupt
line is associated with a specific interrupt vector in the **NVIC**, which determines the handler that
will be executed when an interrupt occurs. For EXTI line 8, it corresponds to a specific interrupt
vector in the **NVIC’s** interrupt vector table, and we need to link this vector to the appropriate ISR,
An ISR (Interrupt Service Routine) is simply the function that gets executed when an interrupt occurs.

![](/interrupts/9.png)

So, in our case, we need to enable interrupt number 23, since EXTI8 falls within the range of EXTI9_5.
This means that `EXTI5`, `EXTI6, ... EXTI9` will let the NVIC know that an interrupt has occurred.
You might be wondering: Can multiple lines trigger the same ISR? How would you know where the interrupt
came from? When you enter the ISR, you won't immediately know whether it was triggered by `EXTI5` or `EXTI6` or something else.
Don't worry, we'll address this issue later and see how to handle it properly.


```c
nvic_enable_irq(NVIC_EXTI9_5_IRQ);
```
![](/interrupts/10.png)

So, what we need now is to place our ISR in the correct location in the vector table. After a bit of searching through the libopencm3 source code, I found that:
![](/interrupts/11.png)


So, we just need to define a function with the same name as the interrupt handler in the vector table. By doing this, we can ensure that the correct ISR is called when the interrupt occurs.
```c
void exti9_5_isr(void) {
    gpio_toggle(GPIOA, GPIO5);
}
```

So, let’s combine everything we know so far:
```c
int main(void) {
  // pin setup
  rcc_periph_clock_enable(RCC_GPIOB);
  gpio_mode_setup(GPIOB, GPIO_MODE_INPUT, GPIO_PUPD_NONE, GPIO8);

  rcc_periph_clock_enable(RCC_GPIOA);
  gpio_mode_setup(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO5);


  // exti setup
  exti_enable_request(EXTI8);
  exti_select_source(EXTI8, GPIOB);

  exti_set_trigger(EXTI8, EXTI_TRIGGER_RISING);

  nvic_enable_irq(NVIC_EXTI9_5_IRQ);

  while(1) {
  }
}


void exti9_5_isr(void) {
    gpio_toggle(GPIOA, GPIO5);
}
```

Well, if you try this, it will not work. A quick look at this will reveal why:
![](/interrupts/12.png)
Remember SYSCFG_EXTCRx, which allowed us to specify that this I/O pin should be linked to a particular EXTIx line? As you can see from the diagram, we need to enable it before the EXTI can properly detect the interrupt from the GPIO pin.

```c
rcc_periph_clock_enable(RCC_SYSCFG);
```

So we end up with:
```c
int main(void) {
  // pin setup
  rcc_periph_clock_enable(RCC_GPIOB);
  gpio_mode_setup(GPIOB, GPIO_MODE_INPUT, GPIO_PUPD_NONE, GPIO8);

  rcc_periph_clock_enable(RCC_GPIOA);
  gpio_mode_setup(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO5);
  
  rcc_periph_clock_enable(RCC_SYSCFG);

  // exti setup
  exti_enable_request(EXTI8);
  exti_select_source(EXTI8, GPIOB);

  exti_set_trigger(EXTI8, EXTI_TRIGGER_RISING);

  nvic_enable_irq(NVIC_EXTI9_5_IRQ);

  while(1) {
  }
}


void exti9_5_isr(void) {
    gpio_toggle(GPIOA, GPIO5);
}
```

So, let’s test it so far. And yes, I haven’t forgotten about the issue where multiple interrupts could lead to the `exti9_5_isr` function.
![](/interrupts/output_test_1.gif)
Don’t worry about all the other wires—they’re there because I was running some tests. The only one you need to care about is the green wire and the green LED.
It kind of works, right? When I press the button, it works, but the second time, it doesn’t turn off. What’s going on?
Well, ask yourself: How does the EXTI know when the interrupt is handled? Shouldn’t it clear the interrupt after it’s been processed?
![](/interrupts/13.png)
So here’s what happens:
We press the button, and **EXTI** sets bit 8 in its pending register, notifying *NVIC*. *NVIC* does
its job, jumps to the `exti9_5_isr`, executes the ISR, and then exits. However, since the pending
bit on **EXTI** is still set (i.e., the interrupt flag hasn’t been cleared), *NVIC* sees that as
another interrupt, and it jumps back into `exti9_5_isr` again.

As a result, the `exti9_5_isr` is being called repeatedly because the interrupt flag isn’t cleared after handling the interrupt.
So why don’t you see the LED blinking even though you’re calling toggle? Well, sorry to say,
your eyes aren’t fast enough to catch it! What’s happening is similar to PWM (Pulse Width Modulation).
The interrupt keeps triggering repeatedly at a fast rate, causing the LED to toggle on and off
so quickly that it appears to be either fully on or fully off, rather than blinking.
so we just need to clear that bit

```c
exti_reset_request(EXTI8);
```

![](/interrupts/14.png)

Here’s the updated version:

```c

void exti9_5_isr(void) {
    gpio_toggle(GPIOA, GPIO5);
    exti_reset_request(EXTI8);
}
```
Well, if you think about it, the pending register can solve the other problem we had. We could read
it and check if the corresponding bit is high. If it is, it means the interrupt was triggered, and
this would tell us which line caused the interrupt.
```c
exti_get_flag_status(EXTI8)
```

![](/interrupts/15.png)

So
```c
void exti9_5_isr(void) {
  if (exti_get_flag_status(EXTI8)) {
    gpio_toggle(GPIOA, GPIO5);
    exti_reset_request(EXTI8);
  }
}
```

Full source code
```c
int main(void) {
  // pin setup
  rcc_periph_clock_enable(RCC_GPIOB);
  gpio_mode_setup(GPIOB, GPIO_MODE_INPUT, GPIO_PUPD_NONE, GPIO8);

  rcc_periph_clock_enable(RCC_GPIOA);
  gpio_mode_setup(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO5 | GPIO6);
  
  rcc_periph_clock_enable(RCC_SYSCFG);

  // exti setup
  exti_enable_request(EXTI8);
  exti_select_source(EXTI8, GPIOB);

  exti_set_trigger(EXTI8, EXTI_TRIGGER_RISING);

  nvic_enable_irq(NVIC_EXTI9_5_IRQ);

  while(1) {
    gpio_toggle(GPIOA, GPIO6);
    for (uint32_t i = 0; i < 1000000; ++i);
  }
}


void exti9_5_isr(void) {
  if (exti_get_flag_status(EXTI8)) {
    gpio_toggle(GPIOA, GPIO5);
    exti_reset_request(EXTI8);
  }
}
```

You might have noticed these changes.
```c
gpio_mode_setup(GPIOA, GPIO_MODE_OUTPUT, GPIO_PUPD_NONE, GPIO5 | GPIO6);
...
...
while(1) {
gpio_toggle(GPIOA, GPIO6);
for (uint32_t i = 0; i < 1000000; ++i);
}
```
These changes are just to demonstrate that the core can handle interrupts independently of the main program.

So, let’s test it out!
![](/interrupts/output_test_2.gif)

#### Sanity Check
Check the enable register of the **EXTI**
![](/interrupts/sc_1.png)
Set the SYSCFG register to select PORTB for EXTI8. This involves configuring the appropriate values to control the select lines of the multiplexer.
![](/interrupts/sc_2.png)
![](/interrupts/sc_2_rf.png)
![](/interrupts/sc_2_rf_1.png)
You may wonder why, when working with EXTI**8**, the first bit is set instead of the 8th one. To understand this, take a closer look at the other pics.

Let’s take a look at the rising edge configuration.
![](/interrupts/sc_3.png)

Enable the NVIC to ensure it "forwards" the interrupts to the core.
![](/interrupts/sc_4.png)

Now, I'm going to press the button and check the pending register of **EXTI**.
![](/interrupts/sc_5.png)

Now, let's move on to the ISR.
![](/interrupts/sc_6.png)

Let's check the reset.
![](/interrupts/sc_7.png)
![](/interrupts/sc_8.png)
Everything seems to be going according to plan.

[repo](https://github.com/Gharbaoui/external_interrupts.git)
#### Questions I would ask if I were you:
- What will happen if multiple interrupts occur at the same time?
- What if I set up multiple interrupts and want to prioritize interrupt A over interrupt B?
- How does the NVIC handle all of this?
- What happens if you are executing critical code, like (Airbag deployment) and an interrupt occurs?
- ...

In the next article, I'll write about them. I was planning to cover it here, but it ended up getting too long and messy.