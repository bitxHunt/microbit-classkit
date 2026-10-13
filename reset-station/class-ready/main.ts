// The "class-ready" program. Every micro:bit gets this after a reset.
// It scrolls the board's own 5-letter name, so anyone can see at a glance
// that the board is reset and which kit it is. It also reports the name
// over the USB cable, so the reset station can log it without typing.
const kitName = control.deviceName()
const serialNumber = control.deviceSerialNumber()

function report() {
    serial.writeLine("KIT " + kitName + " " + serialNumber)
}

report()
basic.forever(function () {
    basic.showString(kitName)
    report()
    basic.pause(1000)
})
