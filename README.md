# Makita battery hack

I created this when trying to hack Makita batteries that had been locked by the famous "three strikes and you're out" feature in an attempt to save them from the scrap bin.

# NEC78K0 Flashing Utility

The repo also contains flashing utility for NEC78K0 MCUs. 

Because 78K0 has no read function we have to improvise. If we can flash our own small piece of code into the processor we can read the flash back using the UART. This envolves finding an empty flash block, by using flash-util, then setting the reset vector to 0x00 and adding our own absolute JMP instruction to our own code that we have placed in an empty block (if existing). If an empty block does not exist, two identical processors are needed in order to get the full flash content.

## Progress

* Recovered original firmware by injecting a trojan to an empty block in the processor and recovering the initiator vector.
* Flashed the recovered firmware back and confirmed that the battery behaved as before.

## TODO

* Reverse engineer the hex dump and figure out what Makita is doing.
* Clean-up the flashing utility.
* Currently only single block flashing is possible with the flash utility. Renesas Flash Programmer V2 can be used to flash multiple blocks but in order to determine empty blocks, injecting the trojan and setting the reset vector, flash utility is neccassary.





[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mnhjansson)

