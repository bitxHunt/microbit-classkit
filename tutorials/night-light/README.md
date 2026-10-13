# Night Light

## Your mission @showdialog

The spaceship gets dark at night. Build a light that switches **itself** on when the room goes dark.

You will work at your own pace. Read each step, build it, then press **Next**.

Stuck? Press the light bulb for a hint.

## Step 1: a choice

Your micro:bit needs to choose: is it dark, or is it bright?

Drag an ``||logic:if then else||`` block into the ``||basic:forever||`` block.

```blocks
basic.forever(function () {
    if (true) {
    	
    } else {
    	
    }
})
```

## Step 2: ask the light sensor

The micro:bit can measure light. 0 is pitch dark, 255 is very bright.

Replace ``true`` with a comparison: ``||input:light level||`` ``<`` ``50``.

```blocks
basic.forever(function () {
    if (input.lightLevel() < 50) {
    	
    } else {
    	
    }
})
```

## Step 3: dark means light on

If it is dark, show a picture. Otherwise, clear the screen.

Put ``||basic:show icon||`` in the top gap and ``||basic:clear screen||`` in the bottom gap.

```blocks
basic.forever(function () {
    if (input.lightLevel() < 50) {
        basic.showIcon(IconNames.Heart)
    } else {
        basic.clearScreen()
    }
})
```

## Stop and predict @showdialog

Before you test it, **guess**:

What will the micro:bit show when you cover it with your hand?

What will it show when you hold it up to the light?

Tell your partner your guess. Then press **Next** and find out.

## Step 4: test it

Look at the micro:bit on the screen. Drag the yellow circle in its corner up and down to change the light.

Was your guess right?

Now send the code to your real micro:bit. Cover it with your hand.

## Add a real lamp @showdialog

Time to add a real LED.

- **Red clip:** from pin **0** to the resistor, then to the LED's **long** leg.
- **Black clip:** from the LED's **short** leg to **GND**.

Push each clip **through the hole**, so it grips the gold pad.

![Wiring: red clip from pin 0 through a resistor to the LED's long leg, black clip from the short leg to GND](https://raw.githubusercontent.com/bitxHunt/microbit-classkit/main/tutorials/night-light/images/wiring-led.png)

## Step 5: switch the lamp on

Pin 0 is where your LED is connected. Writing **1** turns it on. Writing **0** turns it off.

Add ``||pins:digital write pin||`` to both parts of your ``||logic:if then else||``.

```blocks
basic.forever(function () {
    if (input.lightLevel() < 50) {
        basic.showIcon(IconNames.Heart)
        pins.digitalWritePin(DigitalPin.P0, 1)
    } else {
        basic.clearScreen()
        pins.digitalWritePin(DigitalPin.P0, 0)
    }
})
```

## Step 6: change it

Your lamp works. Now make it **yours**.

Change the number ``50``. Try ``20``. Try ``150``. Which number works best in this room?

Pick a different icon for your night light.

## Challenge @showdialog

No steps this time. Can you work it out?

**Add a second LED on pin 1 that turns on when the room is bright**, so one lamp is always on.

Clue: you already know every block you need.

Show your instructor when both lamps work.
