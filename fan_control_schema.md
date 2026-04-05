
Schéma zapojení

+5V (USB/Zdroj) ---------------------+-----------+
                        |            |
                    [Ventilátor]  [D 1N4007] (katoda k +5V)
                        |            |
                        +------------+-----------
                                     |
                                  (Drain)
RPi Pico GP16 ---[ 220R ]------- (Gate)  IRLZ34N
                             |    (Source)
                          [ 10k ]    |
                             |       |
GND -------------------------+-------+----------- GND
