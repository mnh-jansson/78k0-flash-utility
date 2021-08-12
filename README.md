# Makita battery hack

I created this when trying to hack Makita batteries that had been locked by the famous "three strikes and you're out" feature in an attempt to save them from the scrap bin.

# NEC78K0 Flashing Utility

The repo also contains flashing utility for NEC78K0 MCUs. 

## Progress

* Recovered original firmware by injecting a trojan to an empty block in the processor and recovering the initiator vector.
* Flashed the recovered firmware back and confirmed that the battery behaved as before.

## TODO

* Reverse engineer the hex dump and figure out what Makita is doing.
* Clean-up the flashing utility.
* Currently only single block flashing is possible with the flash utility. Renesas Flash Programmer V2 can be used to flash multiple blocks but in order to determine empty blocks, injecting the trojan and setting the reset vector, flash utility is neccassary.