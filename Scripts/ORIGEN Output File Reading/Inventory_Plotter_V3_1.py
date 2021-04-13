################################################################################
# Chad Denbrock
# Editor: Austin Czyzewski
# Niowave Inc.
# Produced: 03.04.2020
# Last updated: 02.10.2021 (AC)
################################################################################

import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl import load_workbook
import matplotlib as mpl
import re
import numpy as np
import time
import pandas as pd
import os
import glob
import xlsxwriter
# Time = time.time()
mpl.rcParams['savefig.dpi']  = 500
mpl.rcParams['font.size']    = 12
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral'

#isotopes halflives list:
isotope_halflives = {"ac224":    10009.999999999998, "ac225":    857100.0, "ac226":    105700.0, "ac227":    687100000.0, "ac228":    22140.0, "ac229":    3762.0, "ag103":    3942.0, "ag104":    4152.0, "ag105":    3567000.0, "ag106m":    715400.0, "ag108m":    13819999999.999998, "ag110m":    21580000.0, "ag111":    643700.0, "ag112":    11270.0, "ag113":    19330.0, "al26":    22630000000000.0, "am237":    4380.0, "am238":    5880.0, "am239":    42840.0, "am240":    182900.0, "am241":    13640000000.000002, "am242":    57670.0, "am242m":    4450000000.0, "am243":    232600000000.0, "am244":    36360.0, "am245":    7380.0, "ar37":    3020000.0, "ar39":    8489000000.000001, "ar41":    6577.0, "ar42":    1038000000.0, "as71":    235000.0, "as72":    93600.0, "as73":    6938000.0, "as74":    1535000.0, "as76":    94540.0, "as77":    139800.0, "as78":    5442.0, "at207":    6480.0, "at208":    5868.0, "at209":    19480.0, "at210":    29160.0, "at211":    25970.0, "au191":    11450.0, "au192":    17780.0, "au193":    63540.0, "au194":    136900.0, "au195":    16080000.000000002, "au196":    532800.0, "au198":    232900.00000000003, "au199":    271200.0, "au200m":    67320.0, "ba126":    6000.0, "ba128":    210000.0, "ba129":    8028.000000000001, "ba129m":    7776.0, "ba130":    3.79e+28, "ba131":    993600.0, "ba133":    331900000.0, "ba133m":    140000.0, "ba135m":    101000.0, "ba139":    4984.0, "ba140":    1102000.0, "ba141":    1100.0, "ba142":    636.0, "ba143":    14.5, "ba144":    11.50, "ba145":    4.31, "ba146":    2.21, "be10":    47650000000000.0, "be7":    4598000.0, "bi201":    6480.0, "bi202":    6192.0, "bi203":    42340.0, "bi204":    40390.0, "bi205":    1323000.0, "bi206":    539400.0, "bi207":    1038000000.0, "bi208":    11610000000000.0, "bi209":    6.343e+26, "bi210":    433000.0, "bi210m":    95940000000000.0, "bi212":    3633.0, "bk243":    16200.000000000002, "bk244":    15660.0, "bk245":    426800.0, "bk246":    155500.0, "bk247":    43550000000.00001, "bk248":    9470000000.0, "bk248m":    85320.0, "bk249":    28510000.0, "bk250":    11560.0, "br75":    5802.0, "br76":    58320.0, "br77":    205300.0, "br80m":    15910.0, "br82":    127000.0, "br83":    8640.0, "br84":    1910.0, "br85":    174.0, "br86":    5.51, "br87":    55.7, "br88":    16.3, "c14":    179900000000.0, "ca41":    3219000000000.0, "ca45":    14050000.0, "ca47":    391900.0, "ca48":    7.258e+26, "cd107":    23400.0, "cd109":    39860000.0, "cd113":    2.4300000000000004e+23, "cd113m":    438000000.0, "cd115":    192000.0, "cd115m":    3850000.0, "cd116":    9.783e+26, "cd117":    8964.0, "cd117m":    12100.0, "ce132":    12640.0, "ce133":    5820.0, "ce133m":    17640.0, "ce134":    273000.0, "ce135":    63720.0, "ce137":    32400.000000000004, "ce137m":    123800.0, "ce139":    11890000.0, "ce141":    2809000.0, "ce142":    1.58e24, "ce143":    118900.0, "ce144":    24620000.000000004, "ce145":    181.0, "ce146":    809.0, "ce147":    56.4, "cf246":    128499.99999999999, "cf247":    11200.000000000002, "cf248":    28809999.999999996, "cf249":    11080000000.000002, "cf250":    412800000.0, "cf251":    28340000000.0, "cf252":    83470000.0, "cf253":    1539000.0, "cf254":    5227000.0, "cf255":    5100.0, "cl36":    9499000000000.0, "cm238":    8640.0, "cm239":    10440.0, "cm240":    2333000.0, "cm241":    2834000.0, "cm242":    14070000.0, "cm243":    918300000.0, "cm244":    571200000.0, "cm245":    268200000000.0, "cm246":    150200000000.0, "cm247":    492300000000000.0, "cm248":    10980000000000.0, "cm249":    3849.0, "cm250":    261900000000.00003, "cm252":    89900.0, "co55":    63110.0, "co56":    6673000.0, "co57":    23480000.0, "co58":    6122000.0, "co58m":    32759.999999999996, "co60":    166300000.0, "co61":    5940.0, "cr48":    77620.0, "cr51":    2393000.0, "cs127":    22500.0, "cs129":    115399.99999999999, "cs131":    837100.0, "cs132":    559900.0, "cs134":    65170000.0, "cs135":    72580000000000.0, "cs136":    1127000.0, "cs137":    947700000.0, "cs138":    1950.0, "cs139":    556.0, "cs140":    63.7, "cs141":    24.84, "cs142":    1.68, "cs143":    1.79, "cu61":    12000.0, "cu64":    45720.0, "cu67":    222600.0, "db266":    4800.0, "db267":    16560.0, "db268":    115199.99999999999, "db270":    3600.0, "dy152":    8568.0, "dy153":    23040.0, "dy154":    94670000000000.0, "dy155":    35640.0, "dy157":    29300.0, "dy159":    12480000.0, "dy165":    8402.0, "dy166":    293800.0, "er158":    8244.0, "er160":    102899.99999999999, "er161":    11560.0, "er163":    4500.0, "er165":    37300.0, "er169":    811500.0, "er171":    27060.0, "er172":    177500.0, "es249":    6132.0, "es250":    30960.0, "es251":    118800.0, "es252":    40750000.0, "es253":    1769000.0, "es254":    23820000.0, "es254m":    141000.0, "es255":    3439000.0, "es256m":    27360.000000000004, "es257":    665300.0, "eu145":    512399.99999999994, "eu146":    398300.0, "eu147":    2081999.9999999998, "eu148":    4709000.0, "eu149":    8044000.000000001, "eu150":    1164000000.0, "eu150m":    46080.0, "eu151":    1.5780000000000002e+26, "eu152":    426199999.99999994, "eu152m":    33520.0, "eu154":    271100000.0, "eu155":    150000000.0, "eu156":    1312000.0, "eu157":    54650.0, "f18":    6585.0, "fe52":    29790.0, "fe55":    86370000.0, "fe59":    3844000.0, "fe60":    82680000000000.0, "fm251":    19080.0, "fm252":    91400.0, "fm253":    259200.0, "fm254":    11660.0, "fm255":    72250.0, "fm256":    9456.0, "fm257":    8683000.0, "ga66":    34160.0, "ga67":    281900.0, "ga68":    4062.9999999999995, "ga72":    50740.0, "ga73":    17500.0, "gd146":    4171000.0000000005, "gd147":    137000.0, "gd148":    2237000000.0, "gd149":    801800.0000000001, "gd150":    56490000000000.0, "gd151":    10710000.0, "gd152":    3.408e+21, "gd153":    20770000.0, "gd159":    66520.0, "ge66":    8135.999999999999, "ge68":    23410000.000000004, "ge69":    140600.0, "ge71":    987600.0, "ge75":    4967.0, "ge76":    5.6420000000000005e+28, "ge77":    40679.99999999999, "ge78":    5280.0, "h3":    388800000.0, "hf170":    57640.0, "hf171":    43560.0, "hf172":    59010000.0, "hf173":    84960.0, "hf174":    6.3120000000000004e+22, "hf175":    6048000.0, "hf180m":    19690.0, "hf181":    3662000.0, "hf182":    280900000000000.03, "hf182m":    3690.0, "hf183":    3841.0, "hf184":    14830.000000000002, "hg192":    17460.0, "hg193":    13680.000000000002, "hg193m":    42480.0, "hg194":    14010000000.0, "hg195":    37910.0, "hg195m":    149800.0, "hg197":    230900.00000000003, "hg197m":    85680.0, "hg203":    4026000.0, "ho160m":    18070.0, "ho161":    8928.0, "ho162m":    4019.9999999999995, "ho163":    144200000000.0, "ho166":    96500.0, "ho166m":    37870000000.0, "ho167":    10810.0, "i120":    4896.0, "i121":    7632.0, "i123":    47600.0, "i124":    360800.0, "i125":    5132000.0, "i126":    1117000.0, "i129":    495500000000000.0, "i130":    44500.0, "i131":    693000.0, "i132":    8262.0, "i132m":    4993.0, "i133":    74880.0, "i134":    3150.0, "i135":    23650.000000000004, "i136":    83.4, "i137":    24.5, "i138":    6.26, "in109":    15120.0, "in110":    17640.0, "in110m":    4146.0, "in111":    242300.0, "in113m":    5968.0, "in114m":    4278000.0, "in115":    1.392e+22, "in115m":    16150.0, "in117m":    6972.0, "ir184":    11120.000000000002, "ir185":    51840.0, "ir186":    59900.0, "ir186m":    6912.0, "ir187":    37800.0, "ir188":    149400.0, "ir189":    1140000.0, "ir190":    1018000.0, "ir190m":    4032.0, "ir192":    6379000.0, "ir192m":    7605000000.0, "ir193m":    909800.0000000001, "ir194":    69410.0, "ir194m":    14770000.0, "ir195":    9000.0, "ir195m":    13680.000000000002, "ir196m":    5040.0, "k40":    3.938e+16, "k42":    44360.0, "k43":    80280.0, "kr76":    53280.0, "kr77":    4464.0, "kr78":    2.8999999999999996e+29, "kr79":    126099.99999999999, "kr81":    7227000000000.0, "kr85":    338400000.0, "kr85m":    16130.0, "kr87":    4578.0, "kr88":    10220.0, "kr89":    189.0, "kr90":    32.3, "kr91":    8.57, "la132":    17280.0, "la133":    14080.0, "la135":    70200.0, "la137":    1893000000000.0, "la138":    3.219e+18, "la140":    145000.0, "la141":    14110.0, "la142":    5466.0, "la143":    852.0, "la144":    40.8, "la145":    24.8, "lr262":    12960.0, "lr266":    36000.0, "lu169":    122600.0, "lu170":    173800.0, "lu171":    711900.0, "lu172":    578900.0, "lu173":    43230000.00000001, "lu174":    104500000.0, "lu176":    1.187e+18, "lu176m":    13190.0, "lu177":    574300.0, "lu177m":    13859999.999999998, "lu179":    16520.0, "m119":    25339999.999999996, "m152":    5760.0, "m154":    35980.0, "m154":    81720.0, "m156":    19080.0, "m174":    12270000.0, "m178":    977600000.0, "m179":    2164000.0, "m190":    11110.0, "m196":    34560.0, "m198":    196000.0, "m204":    4016.0, "m83":    6588.0, "md256":    4620.0, "md257":    19870.0, "md258":    4450000.0, "md259":    5760.0, "md260":    2748000.0, "mg28":    75290.0, "mn52":    483100.00000000006, "mn53":    118000000000000.0, "mn54":    26970000.0, "mn56":    9284.0, "mo100":    2.461e+26, "mo90":    20019.999999999996, "mo93":    126200000000.0, "mo93m":    24660.000000000004, "mo99":    237500.0, "mo101":    877.0, "mo102":    678.0, "mo103":    67.5, "mo104":    60.0, "mo105":    35.6, "mo106":    8.73, "na22":    82129999.99999999, "na24":    53820.0, "nb89":    7308.0, "nb89m":    3960.0, "nb90":    52560.0, "nb91":    21460000000.0, "nb91m":    5258000.0, "nb92":    1095000000000000.0, "nb92m":    877000.0, "nb93m":    508399999.99999994, "nb94":    640600000000.0, "nb95":    3023000.0, "nb95m":    311000.0, "nb96":    84060.0, "nb97":    4326.0, "nb97m":   58.7, "nb98":    2.86, "nb99":    15.0, "nb99m":    150.0, "nb100":    1.5, "nb101":    7.1, "nb102":    4.3, "nb103":    1.5, "nd138":    18140.0, "nd139m":    19800.0, "nd140":    291200.0, "nd141":    8964.0, "nd144":    7.227e+22, "nd147":    948700.0, "nd149":    6221.0, "nd150":    2.493e+26, "ni56":    524900.0, "ni57":    128200.0, "ni59":    2398000000000.0, "ni63":    3159000000.0, "ni65":    9062.0, "ni66":    196600.0, "np234":    380200.0, "np235":    34220000.0, "np236":    4860000000000.0, "np236m":    81000.0, "np237":    67660000000000.0, "np238":    182900.0, "np239":    203600.0, "np240":    3714.0, "os181":    6300.0, "os182":    79560.0, "os183":    46800.0, "os183m":    35640.0, "os185":    8087000.0, "os186":    6.3120000000000004e+22, "os189m":    20920.0, "os191":    1331000.0, "os191m":    47160.0, "os193":    108400.00000000001, "os194":    189300000.0, "os195m":    7200.0, "p32":    1232000.0, "p33":    2189000.0, "pa228":    79200.0, "pa229":    129600.0, "pa230":    1503000.0, "pa231":    1034000000000.0, "pa232":    113199.99999999999, "pa233":    2331000.0, "pa234":    24120.0, "pa239":    6480.0, "pb198":    8640.0, "pb199":    5400.0, "pb200":    77400.0, "pb201":    33590.0, "pb202":    1657000000000.0, "pb202m":    12740.0, "pb203":    186900.0, "pb205":    545899999999999.94, "pb209":    11710.0, "pb210":    700600000.0, "pb212":    38300.0, "pd100":    313600.0, "pd101":    30490.0, "pd103":    1468000.0, "pd107":    205100000000000.03, "pd109":    49320.00000000001, "pd111m":    19800.0, "pd112":    75710.0, "pm143":    22900000.0, "pm144":    31360000.0, "pm145":    558600000.0, "pm146":    174500000.0, "pm147":    82790000.0, "pm148":    463800.0, "pm148m":    3567000.0, "pm149":    191100.0, "pm150":    9648.0, "pm151":    102200.0, "po204":    12709.999999999998, "po205":    6264.0, "po206":    760300.0, "po207":    20880.0, "po208":    91450000.0, "po209":    3951000000.0, "po210":    11960000.0, "pr137":    4608.0, "pr138m":    7632.0, "pr139":    15880.0, "pr142":    68830.0, "pr143":    1172000.0, "pr144":    1040.0, "pr145":    21540.0, "pr146":    1450.0, "pr147":    804.0, "pt185":    4254.0, "pt186":    7488.0, "pt187":    8460.0, "pt188":    881300.0000000001, "pt189":    39130.0, "pt190":    2.051e+19, "pt191":    247300.0, "pt193":    1578000000.0, "pt193m":    374000.0, "pt195m":    346000.0, "pt197":    71610.0, "pt197m":    5725.0, "pt200":    45000.0, "pt202":    158400.0, "pu234":    31680.0, "pu236":    90190000.0, "pu237":    3905000.0, "pu238":    2768000000.0, "pu239":    760900000000.0, "pu240":    206999999999.99997, "pu241":    451000000.0, "pu242":    11830000000000.0, "pu243":    17840.0, "pu244":    2525000000000000.0, "pu245":    37800.0, "pu246":    936600.0, "pu247":    196100.0, "ra223":    987600.0, "ra224":    313800.0, "ra225":    1287000.0, "ra226":    50490000000.0, "ra228":    181500000.0, "ra230":    5580.0, "rb81":    16450.0, "rb82m":    23300.0, "rb83":    7448000.0, "rb84":    2860000.0, "rb86":    1611000.0, "rb87":    1.568e+18, "rb88":    1070.0, "rb89":    919.0, "rb90":    158.0, "rb91":    58.2, "rb92":    4.48, "rb93":    5.84, "re181":    71640.0, "re182":    230399.99999999997, "re182m":    45720.0, "re183":    6048000.0, "re184":    3059000.0, "re184m":    14600000.0, "re186":    321000.0, "re186m":    6312000000000.0, "re187":    1.3e+18, "re188":    61210.00000000001, "re189":    87480.0, "re190m":    11520.0, "rf267":    8280.0, "rh100":    74880.0, "rh101":    104099999.99999999, "rh101m":    374000.0, "rh102":    17880000.0, "rh102m":    91519999.99999999, "rh103m":    3370.0, "rh105":    127299.99999999999, "rh106m":    7860.0, "rh99":    1391000.0, "rh99m":    16920.0, "rn210":    8640.0, "rn211":    52560.0, "rn222":    330400.0, "rn224":    6420.0, "ru103":    3392000.0, "ru105":    15980.0, "ru106":    32280000.000000004, "ru95":    5915.0, "ru97":    241100.0, "s35":    7561000.0, "s38":    10220.0, "sb116m":    3618.0, "sb117":    10080.0, "sb118m":    18000.0, "sb119":    137500.0, "sb120m":    497700.00000000006, "sb122":    235300.00000000003, "sb124":    5194000.0, "sb125":    87050000.0, "sb126":    1067000.0, "sb127":    332600.0, "sb128":    32440.000000000004, "sb129":    15840.0, "sb130":    2370.0, "sb131":    1380.0, "sb132":    167.0, "sb133":    140.0, "sc43":    14010.0, "sc44":    14290.0, "sc44m":    211000.0, "sc46":    7239000.0, "sc47":    289400.0, "sc48":    157200.0, "se72":    725800.0, "se73":    25740.0, "se75":    10350000.0, "se79":    9309000000000.0, "se82":    3.408e+27, "si31":    9438.0, "si32":    4166000000.0000005, "sm134":    10480.0, "sm142":    4349.0, "sm145":    29380000.0, "sm146":    2144000000000000.2, "sm147":    3.345e+18, "sm148":    2.209e+23, "sm150":    7992.0, "sm151":    2840000000.0, "sm153":    166600.0, "sm156":    33840.0, "sn110":    14800.0, "sn113":    9944000.0, "sn117m":    1210000.0, "sn121":    97300.0, "sn121m":    1385000000.0, "sn123":    11160000.000000002, "sn125":    832900.0000000001, "sn126":    7258000000000.0, "sn127":    7560.0, "sr80":    6378.0, "sr82":    2208000.0, "sr83":    116700.0, "sr85":    5602000.0, "sr85m":    4058.0, "sr87m":    10129.999999999998, "sr89":    4369000.0, "sr90":    911999999.9999999, "sr91":    34670.0, "sr92":    9576.0, "sr93":    446.0, "sr94":    75.3, "sr95":    23.9, "sr96":    1.07, "sr97":    0.429, "ta173":    11299.999999999998, "ta174":    4104.0, "ta175":    37800.0, "ta176":    29120.0, "ta177":    203600.0, "ta178m":    8496.0, "ta179":    57430000.0, "ta180":    29350.0, "ta182":    9887000.0, "ta183":    440599.99999999994, "ta184":    31320.0, "tb147":    6120.0, "tb148":    3600.0, "tb149":    14820.0, "tb150":    12529.999999999998, "tb151":    63390.00000000001, "tb152":    63000.0, "tb153":    202199.99999999997, "tb154":    77400.0, "tb155":    459600.0, "tb156":    462200.0, "tb156m":    87800.0, "tb157":    2241000000.0, "tb158":    5680000000.0, "tb160":    6247000.0, "tb161":    596700.0, "tc93":    9900.0, "tc94":    17580.0, "tc95":    72000.0, "tc95m":    5270000.0, "tc96":    369800.0, "tc97":    132900000000000.0, "tc97m":    7862000.0, "tc98":    132500000000000.0, "tc99":    6662000000000.0, "tc99m":    21620.0, "tc100":    15.5, "tc101":    853.0, "tc102":    5.28, "tc103":    54.2, "tc104":    1100.0, "tc105":    456.0, "te116":    8964.0, "te117":    3720.0, "te118":    518400.0, "te119":    57779.99999999999, "te119m":    406100.0, "te121":    1656000.0, "te121m":    13310000.0, "te123m":    10300000.0, "te125m":    4959000.0, "te127":    33660.0, "te127m":    9418000.0, "te128":    6.9400000000000005e+31, "te129":    4176.0, "te129m":    2903000.0, "te130":    2.7770000000000002e+26, "te131":    1500.0, "te131m":    108000.0, "te132":    276800.0, "te133":    750.2, "te133m":    3320.0, "te134":    2510.0, "te135":    19.0, "th227":    1614000.0, "th228":    60330000.0, "th229":    231599999999.99997, "th230":    2379000000000.0, "th231":    91870.0, "th232":    4.434e+17, "th234":    2081999.9999999998, "ti44":    1893000000.0, "ti45":    11090.0, "tl195":    4176.0, "tl196":    6624.0, "tl196m":    5076.0, "tl197":    10220.0, "tl198":    19080.0, "tl198m":    6732.0, "tl199":    26710.0, "tl200":    93960.00000000001, "tl201":    262500.0, "tl202":    1057000.0, "tl204":    119300000.0, "tm163":    6516.0, "tm165":    108200.00000000001, "tm166":    27719.999999999996, "tm167":    799200.0, "tm168":    8044000.000000001, "tm170":    11110000.0, "tm171":    60590000.0, "tm172":    229000.0, "tm173":    29660.000000000004, "u230":    1797000.0, "u231":    362900.0, "u232":    2174000000.0, "u233":    5024000000000.0, "u234":    7747000000000.0, "u235":    2.222e+16, "u236":    739100000000000.0, "u237":    583200.0, "u238":    1.41e+17, "u239":    1410.0, "u240":    50759.99999999999, "v48":    1380000.0, "v49":    28430000.0, "v50":    4.418e+24, "w176":    9000.0, "w177":    7920.0, "w178":    1866000.0, "w180":    5.6800000000000005e+25, "w181":    10470000.0, "w185":    6489000.0, "w187":    85390.0, "w188":    6029000.0, "xe122":    72360.0, "xe123":    7488.0, "xe124":    5.679999999999999e+29, "xe125":    60839.99999999999, "xe127":    3145000.0, "xe129m":    767200.0, "xe131m":    1022999.9999999999, "xe133":    453000.0, "xe133m":    189000.0, "xe135":    32900.0, "xe136":    7.5e+28, "xe137":    229.0, "xe138":    848.0, "xe139":   39.7, "xe140":    13.6, "y85":    9648.0, "y85m":    17500.0, "y86":    53060.0, "y87":    287300.0, "y87m":    48130.0, "y88":    9212000.0, "y90":    230600.0, "y90m":    11480.0, "y91":    5055000.0, "y91m":    2980.0, "y92":    12740.0, "y93":    36650.0, "y93m":    0.82, "y94":    1120.0, "y95":    618.0, "y96":    5.34, "y96m":    9.6, "y97":    3.75, "y98":    2.0, "yb164":    4548.0, "yb166":    204100.0, "yb169":    2767000.0, "yb175":    361600.0, "yb177":    6880.0, "yb178":    4440.0, "zn62":    33070.0, "zn65":    21050000.0, "zn69m":    49540.0, "zn71m":    14260.0, "zn72":    167400.0, "zr86":    59400.00000000001, "zr87":    6048.0, "zr88":    7206000.0, "zr89":    282300.0, "zr93":    48280000000000.0, "zr95":    5532000.0, "zr96":    6.3e+26, "zr97":    60279.99999999999, "zr98":    30.7, "zr99":    2.1, "zr100":    7.1, "zr101":    2.3, "kr83m": 6588.0, "sn128": 3544.2000000000003, "se81m": 3436.8000012, "nb98m": 3078.0, "eu158": 2754.0, "in117": 2592.0, "sn123m": 2403.6000012, "pd111": 1404.0, "se83": 1338.0000012, "sm155": 1338.0000012, "rh107": 1302.0000012, "ag115": 1199.9999988, "sb126m": 1149.0000012, "se81": 1107.0, "eu159": 1086.0000012, "in119m": 1080.0, "xe135m": 917.3999987999999, "nd151": 746.3999988, "nd152": 684.0, "sb128m": 623.9999988000001, "sn125m": 571.2000012000001, "as79": 540.6000012000001, "sm157": 482.00000040000003, "pr144m": 432.0, "sn129m": 414.0, "sb130m": 378.0, "br84m": 360.0, "sm158": 317.9999988, "pm153": 315.0, "ru108": 272.9999988, "tc102m": 261.0, "rb90m": 258.0000012, "sn127m": 247.7999988, "pm152": 247.2000012, "sb132m": 245.9999988, "se79m": 235.19999879999997, "in121m": 232.8000012, "ru107": 225.0, "sn130": 223.2, "i134m": 216.0, "se84": 186.00000119999999, "cd119": 161.39999880000002, "ag116": 160.8000012, "pm154m": 160.8000012, "ba137m": 153.1199988, "pd114": 145.1999988, "in119": 144.0, "pr149": 135.6000012, "sn129": 133.8000012, "cd119m": 132.0000012, "ga75": 126.00000000000001, "pr148m": 119.9999988, "pm154": 103.7999988, "sn130m": 101.9999988, "pd113": 92.9999988, "rh109": 79.9999992, "ag117": 72.7999992, "se83m": 70.0999992, "ag113m": 68.6999988, "ag111m": 64.8, "sn131": 56.0000016, "ce148": 56.0000016, "ge77m": 52.899998399999994, "in123m": 47.8000008, "i136m": 46.9000008, "in120m": 46.1999988, "rh105m": 45.0, "pm155": 41.5000008, "sn132": 39.7000008, "ag109m": 39.599999999999994, "ge79m": 38.9999988, "tc106": 35.6000004, "ru109": 34.4999988, "as81": 33.3, "ga76": 32.6000016, "se85": 31.700001600000004, "nd153": 31.6000008, "rh106": 29.8000008, "ge80": 29.499998400000003, "pm156": 26.7000012, "nd154": 25.8999984, "pd115": 24.9999984, "in121": 23.1000012, "tc107": 21.200000399999997, "as82": 19.100001600000002, "cs138m": 19.000000800000002, "ge79": 18.9799992, "pr151": 18.900000000000002, "ag115m": 18.0, "te136": 17.499999600000002, "rh108": 16.8000012, "se86": 15.3, "as80": 15.1999992, "ru110": 14.6000016, "as82m": 13.6000008, "cd121": 13.5, "as83": 13.3999992, "ga77": 13.2000012, "in125m": 12.2000004, "pd116": 11.8000008, "rh111": 11.000001600000001, "pm157": 10.5599988, "in122m": 10.2999996, "sb134m": 10.2300012, "la146m": 10.000000799999999, "i133m": 9.0, "nd155": 8.8999992, "ag116m": 8.600000399999999, "cd121m": 8.3000016, "ge81": 7.5999996, "sn128m": 6.5000016, "la146": 6.270001199999999, "pr150": 6.1899984, "in123": 5.9799996, "zn76": 5.6999987999999995, "nd156": 5.4699984, "ag117m": 5.3399988, "ce149": 5.2999992, "se87": 5.2899984, "tc108": 5.1699996, "ga78": 5.0900004, "in118": 5.000000399999999, "ge82": 4.6000008, "ag114": 4.6000008, "as84": 4.5, "br89": 4.3480008, "nb102m": 4.2999984, "pd117": 4.2999984, "pr153": 4.2800004000000005, "la147": 4.0150008, "ag118": 3.7599984, "in124m": 3.7000008, "in127m": 3.6699984, "pr152": 3.6299987999999996, "mo107": 3.4999992, "rh110": 3.2000004, "in124": 3.1100003999999997, "in120": 3.0800016, "nb100m": 2.9900016, "nb105": 2.9499984, "zr102": 2.9000016, "ga79": 2.8469988, "rh113": 2.8000008000000003, "rb94": 2.7020016, "te137": 2.4900012, "in125": 2.3600016, "pr154": 2.3000004, "i139": 2.2899996, "ru111": 2.1200004, "rh112": 2.0999988, "ag119": 2.0999988, "cd123": 2.0999988, "zn77": 2.0800008, "as85": 2.0210004, "y98m": 2.0000016, "ag118m": 2.0000016, "br90": 1.9100015999999997, "pd118": 1.9000008000000002, "ge83": 1.8500004, "rh114": 1.8500004, "kr92": 1.8399995999999998, "ru112": 1.7499996, "xe141": 1.7300016, "sb135": 1.71, "ga80": 1.6970004, "in126m": 1.6400016, "in126": 1.5999984, "se88": 1.5299999999999998, "in122": 1.5000012, "zn78": 1.4699988, "y99": 1.4699988, "sn133": 1.4500008, "ce152": 1.4000004000000001, "zr103": 1.2999996, "kr93": 1.2859992, "cd124": 1.2499992, "ag120": 1.2300012, "in129m": 1.2300012, "xe142": 1.2200004, "ga81": 1.2170016, "zr104": 1.1999988, "sn134": 1.1199995999999999, "mo108": 1.0900008, "in127": 1.0900008, "la148": 1.0500012, "nb106": 1.0199988, "cs144": 1.0100016, "zn79": 0.9950003999999999, "rh115": 0.9900000000000001, "ge84": 0.9470016, "nb104m": 0.9200016, "tc110": 0.9200016, "ba147": 0.8930016000000001, "tc109": 0.8700011999999999, "i140": 0.8600004, "in128": 0.8399988, "ru113": 0.7999992, "ag121": 0.7800012000000001, "sb134": 0.7800012000000001, "y100": 0.7350012, "in128m": 0.7200000000000001, "sr98": 0.6530004, "cd125": 0.6500016000000001, "in129": 0.6099984, "ba148": 0.6069996, "ga82": 0.5990004, "cs145": 0.594, "br91": 0.5410008, "ge85": 0.5349996, "ru114": 0.5299992, "cd126": 0.5060015999999999, "pd120": 0.5000004, "y101": 0.45, "rb95": 0.3774996, "cd127": 0.3700008, "y102": 0.36000000000000004, "br92": 0.34300008000000004, "cd128": 0.33999984, "cs146": 0.32100012, "in130": 0.32000004, "mo110": 0.29999988, "tc111": 0.29999988, "xe134m": 0.29000016, "in131": 0.28199988000000004, "sr99": 0.26899992, "y103": 0.23000004000000002, "cs147": 0.225, "sr100": 0.20199996, "in132": 0.20099988, "kr94": 0.20000016, "rb96": 0.19900008, "rb97": 0.16989984000000002, "sr101": 0.11800008000000001, "rb98": 0.11400012, "rb100": 0.051000119999999996}

# print(isotope_halflives['nb100m'])

################################################################################
# Goal: Plot a fission product/actinide inventory from UTA-2 for a given
#           irradiation/decay cycle.
#
#
# Requirements: (Outdated)
#       Two excel (.xlsx) files. One for each the NU and LEU portions of UTA-2.
#           They must be named with 'NU' and 'LEU' being the beginning characters
#           in the file like 'NU blah blah.xlsx' and 'LEU blah blah.xlsx'. These
#           excel files must be copy and pasted acitivities as a function of time
#           from F71 output files from Origen. This includes the isotope names
#           being the column names with the activities as a function of time
#           progressing in the rows in the column. The irradiation/decay cycle
#           for the NU and LEU obviously must be the same for the two excel
#           documents. The NU and LEU inventories will inveitably have different
#           isotopes in their inventory. This is not a problem.
#       The 'Half_Lives_List.txt' half-life library used to check whether the
#           isotopes have a half-life less than or greater than or equal to
#           120 days.
################################################################################

#   No 100 gNU MCNP calculations were performed for the optimized UTA-2 configuration
# def convert_to_100gNU(NU) :
#
#     fraction_FP_and_An_in_100gNU_over_total_NU = 0.01743
#     fraction_U237_in_100gNU_over_total_NU = 0.03485
#
#     Time = NU['Unnamed: 0']
#     NU = NU.drop(columns = 'Unnamed: 0')
#     Updated_Inventory = NU*fraction_FP_and_An_in_100gNU_over_total_NU
#     if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
#         Updated_Inventory['u237'] = Updated_Inventory['u237']*fraction_U237_in_100gNU_over_total_NU/fraction_FP_and_An_in_100gNU_over_total_NU
#     Updated_Inventory = pd.DataFrame.sort_values(Updated_Inventory,Updated_Inventory.shape[0]-1,axis=1,ascending=False)
#     Updated_Inventory.insert(loc=0,column = f'Time ({time_units})',value = Time)
#
#     print('Writing updated inventory to Inventory_Hottest_100gNU.xlsx ...\n')
#
#     while True :
#         try :
#             Updated_Inventory.to_excel('Inventory_Hottest_100gNU.xlsx')
#             break
#         except :
#             print('There was a problem with writing Inventory_Hottest_100gNU.xlsx. '\
#                 'It may already exist. Delete it if it does. The script will try to '\
#                 'write it again in 15 seconds.\n')
#             time.sleep(15)
#     return Updated_Inventory

def convert_to_1kgNU(NU, time_units) :

    Mass_per_rod_gU = 134.6
    Rods_per_1kgNU = 1000/Mass_per_rod_gU
    scaling = Rods_per_1kgNU/7


    fraction_FP_and_An_in_7rods_over_total_NU = 0.1187849
    fraction_U237_in_7rods_over_total_NU = 0.3376
    
    print(f'Assumptions made:'\
         f'Mass per rod: {Mass_per_rod_gU:.2f} grams'\
          f'Fraction of fission products and actinides in 7 rods over total NU: {fraction_FP_and_An_in_7rods_over_total_NU:.6f}'\
          f'Fraction of U-237 in 7 rods over total NU: {fraction_U237_in_7rods_over_total_NU:.4f}')

    fraction_FP_and_An_in_1kgNU_over_total_NU = fraction_FP_and_An_in_7rods_over_total_NU * scaling     # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU
    fraction_U237_in_1kgNU_over_total_NU = fraction_U237_in_7rods_over_total_NU * scaling               # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU

    Time = NU['Time ({})'.format(time_units)]
    NU = NU.drop(columns = 'Time ({})'.format(time_units))
    Updated_Inventory = NU*fraction_FP_and_An_in_1kgNU_over_total_NU

    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
        Updated_Inventory['u237'] = Updated_Inventory['u237']*fraction_U237_in_1kgNU_over_total_NU/fraction_FP_and_An_in_1kgNU_over_total_NU
#     Updated_Inventory = pd.DataFrame.sort_values(Updated_Inventory,Updated_Inventory.shape[0]-1,axis=1,ascending=False)
#     Updated_Inventory["Total_Activity"] = Updated_Inventory.iloc[:, 1:].sum(axis = 1)
#     print("AHH")
#     print(Updated_Inventory['Total_Activity'])
#     Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.index[Updated_Inventory.shape[0]-1], axis = 1, ascending = False) #Added by Austin to replace the above commented out line
#     Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.iloc[-1], axis = 0, ascending = False) #Added by Austin to replace the above commented out line
    Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.iloc[-1].name, axis = 1, ascending = False)
    Updated_Inventory.insert(loc=0,column = f'Time ({time_units})',value = Time)

    print('Writing updated inventory to The_Hottest_1kgNU_Inventory.xlsx ...')
    print("This may take a few minutes ...\n")
    while True :
        try :
            Updated_Inventory.to_excel('The_Hottest_1kgNU_Inventory.xlsx')
            break
        except :
            print('There was a problem with writing The_Hottest_1kgNU_Inventory.xlsx. '\
                'It may already exist. Delete it if it does. The script will try to '\
                'write it again in 15 seconds.\n')
            time.sleep(15)
    return Updated_Inventory

def U_237_adder(NU,LEU, time_units) :

    fraction_U_237_in_LEU = 0.737
    fraction_U_237_in_NU = 1.0 - fraction_U_237_in_LEU
    Total_core_reaction_rate_per_e = 2.386e-4     # Total U-237 reactions/e for 20 MeV electrons in traditional UTA-2 geometry
    Electron_rate = 2.184e15
    print(f'The total core reaction rate per electron for U-237 production '\
        f'{Total_core_reaction_rate_per_e:.3e} and the electron source intensity '\
        f'{Electron_rate:.3e} are hardcoded in for a 20 MeV electron beam and need to be changed for alternate '\
        'configurations of UTA-2.\n'\
        'The neutron flux to achieve the ORIGEN results and the electron rate to '\
        'achieve the U-237 production are no longer physically linked. So, be '\
        'careful and make sure the hardcoded electron rate corresponds to the '\
        'electron rate necessary to produce the fission power input into ORIGEN.')
    

    Total_core_reaction_rate = Electron_rate * Total_core_reaction_rate_per_e


    half_life_U_237 = 6.752*86400
    lambda_U_237 = np.log(2)/half_life_U_237
    
    print("-"*80 + "\nAssumptions made for U-237:")
    print(f'Fraction of U-237 in LEU: {fraction_U_237_in_LEU:.3f}\n'\
         f'Fraction of U-237 in NU: {fraction_U_237_in_NU:.3f}\n'\
         f'Total Core reaction rate per electron: {Total_core_reaction_rate_per_e:.3E}\n'\
         f'Electron Rate: {Electron_rate:.3E}\n'\
         f'The half life of U-237: {half_life_U_237:.3f}\n\n')
    
    try :
        test_activity = pd.Series.to_numpy(LEU['np239'],dtype = 'float')
    except :
        print('Np239 doesnt exist in the LEU spreadsheet. This probably means you incorrectly asked for what youre plotting.\n')
        exit()
    
    Time = pd.Series.to_numpy(NU['Time ({})'.format(time_units)],dtype = 'float')
#     print("Time ",len(Time))
#     print(NU['ac224'])
#     if time_units.lower() == 'years' :
#         dt_multiplier = 86400*365.25

#     elif time_units.lower() == 'days' :
#         dt_multiplier = 86400.0
    if time_units == 'years':
        dt_multiplier = 86400*365.25

    elif time_units == 'days':
        dt_multiplier = 86400.0

    U_237 = np.zeros(len(Time))


    growth_guess = 0
    first_guess_completed = False

    for time_values in range(len(Time)-1) :


        if test_activity[time_values] == 0 or (test_activity[time_values+1] - test_activity[time_values])/test_activity[time_values] >= growth_guess:

            dt = (Time[time_values + 1] - Time[time_values])*dt_multiplier
            dU_237 = (Total_core_reaction_rate - lambda_U_237*U_237[time_values])*dt

        else :

            if first_guess_completed == False :
                growth_guess = (test_activity[time_values-1] - test_activity[time_values])/(50*test_activity[time_values-1])
                first_guess_completed = True


            dt = (Time[time_values + 1] - Time[time_values])*dt_multiplier
            dU_237 =                           - lambda_U_237*U_237[time_values]*dt

#         if time_units == 'Years' and (Time[time_values] == 4.006471 or Time[time_values] ==4.004729):
        if time_units == 'years' and (Time[time_values] == 4.006471 or Time[time_values] ==4.004729):
            #print('\nin here\n')
            dU_237 = 0.0
        #print(Time[time_values],test_activity[time_values+1] - test_activity[time_values],dU_237,U_237[time_values],dt)

        U_237[time_values+1] = U_237[time_values] + dU_237
    U_237 = U_237 * lambda_U_237/3.7e10
#     print("U237 ",len(U_237))

    #plt.plot(Time,U_237)
    #plt.plot(Time,U_237*fraction_U_237_in_NU)
    #plt.plot(Time,U_237*fraction_U_237_in_LEU)
    #plt.show()

    if 'u237' not in NU.columns:
#         print('False ',len(U_237*fraction_U_237_in_NU))
        NU.insert(loc = 1,column = 'u237',value=U_237*fraction_U_237_in_NU)
    else :
#         print('True ',len(U_237*fraction_U_237_in_NU))
        U_237_Col = U_237*fraction_U_237_in_NU + NU.u237
        #print(U_237_Col)
#         NU = NU.add(pd.DataFrame(U_237*fraction_U_237_in_NU,columns = ['u237']),fill_value = 0)
        NU.u237 = U_237_Col

    if 'u237' not in LEU.columns:
#         print('False ',len(U_237*fraction_U_237_in_LEU))
        LEU.insert(loc = 1,column = 'u237',value=U_237*fraction_U_237_in_LEU)
    else :
#         print('True ',len(U_237*fraction_U_237_in_LEU))
        U_237_Col = U_237*fraction_U_237_in_LEU + LEU.u237
        #print(U_237_Col)
#         LEU = LEU.add(pd.DataFrame(U_237*fraction_U_237_in_LEU,columns = ['u237']),fill_value = 0)
        LEU.u237 = U_237_Col
    return NU,LEU


def plotting(The_Inventory):
    eff_list = ['kr85m','kr88','kr85','kr87','i131','i132','i133','i135','xe133','xe133m','xe135']
    Input = list()


    Splitting = True    # Choosing to always split the inventories for plotting purposes

#       Asking for what to plot (totals or specific isotopes)
    top_regex = '[Tt]op [0-9]+'
    while True :
        #try :
        Input.append(input('Name isotopes you wish to plot. You can also plot the total by typing \'Total\', the top x isotopes by activity at final time by typing \'Top <integer number of isotopes you want to see>\', or the effluents list by typing \'Effluents\'. (Hit enter after each one and type \'Stop\' to quit entering isotopes)\n').lower())
        if Input[-1].lower() == 'effluents' :
            Input = Input[:-1] + eff_list
        if len(re.findall(top_regex,Input[-1])) > 0:
            top_quantity = int(Input[-1].split()[1])
            Input = Input[:-1] + list(The_Inventory.columns[3:top_quantity+3])
        if Input[-1].lower() == 'stop' :
            Input = Input[:-1]
            break
        #except :
            #print('Try that again. Make sure to hit enter after each entry. The form should be: \'np239\'\n')



    Greater_than,Less_than = split_120(The_Inventory)     # Split the inventory by half-lives and retrieve the time vector
#     print("####DID I MAKE IT HERE???####")
    Time = The_Inventory[f'Time ({time_units})']
    print("\n")

    if 'total' in Input:
        # -----------------------
        # Plotting both HL's
        # -----------------------
        plt.plot(Time,Less_than['Total'])
        if len(Greater_than['Total']) > 0:
            plt.plot(Time,Greater_than['Total'])
        legend_list = ['Half Life < 120 d','Half Life > 120 d']
#         for vals in Input :
#             if vals != 'total'  :
#                 legend_list.append(vals)
        #plt.show()
        if len(Greater_than['Total']) > 0:
            max = (Greater_than['Total'] + Less_than['Total']).max()
            end = pd.Series.to_numpy(Greater_than['Total'] + Less_than['Total'])[-1]
            print(f'\nThe max Total activity was {max:.3f} (Ci)')
            print(f'The final Total activity was {end:.3f} (Ci)')
            max = Greater_than['Total'].max()
            end = pd.Series.to_numpy(Greater_than['Total'])[-1]
            print(f'The max activity (HL > 120 d) was {max:.3f} (Ci)')
            print(f'The final activity (HL > 120 d) was {end:.3f} (Ci)')
            max = Less_than['Total'].max()
            end = pd.Series.to_numpy(Less_than['Total'])[-1]
            print(f'The max activity (HL < 120 d) was {max:.3f} (Ci)')
            print(f'The final activity (HL < 120 d) was {end:.3f} (Ci)')
        else :
            max = Less_than['Total'].max()
            end = pd.Series.to_numpy(Less_than['Total'])[-1]
            print(f'The max total activity was {max:.3f} (Ci)')
            print(f'The final total activity was {end:.3f} (Ci)\n')
        for vals in Input :
            try:
                if vals != 'total'  :

                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                    print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                    print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
                    legend_list.append(vals)
            except:
                print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue
                
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title}')
        plt.xlabel(time_units.capitalize())
        plt.ylabel('Activity (Ci)')
        plt.savefig(fname + '_Both.png',bbox_inches = 'tight')
        print(f'\nFigure {fname}_Both.png produced and saved.\n')
        plt.close()
        # -----------------------
        # Plotting HL >
        # -----------------------
        if len(Greater_than['Total']) > 0:
            plt.plot(Time,Greater_than['Total'])
            legend_list = ['Half Life > 120 d']
            for vals in Input :
                try:
                    if vals != 'total':
                        #plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                        plt.plot(Time,pd.Series.to_numpy(Greater_than[vals]))
                        legend_list.append(vals)
                except :
                    #print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                    continue
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title} (HL > 120 days)')
            plt.xlabel(time_units.capitalize())
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname + '_Greaterthan.png',bbox_inches = 'tight')
            print(f'\nFigure {fname}_Greaterthan.png produced and saved.\n')
            plt.close()
        # -----------------------
        # Plotting HL <
        # -----------------------
        plt.plot(Time,Less_than['Total'])
        legend_list = ['Half Life < 120 d']
        for vals in Input :
            try:
                if vals != 'total'  :
                    plt.plot(Time,pd.Series.to_numpy(Less_than[vals]))
                    legend_list.append(vals)
            except :
                #print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title} (HL < 120 days)')
        plt.xlabel(time_units.capitalize())
        plt.ylabel('Activity (Ci)')
        plt.savefig(fname + '_Lessthan.png',bbox_inches = 'tight')
        print(f'\nFigure {fname}_Lessthan.png produced and saved.\n')
        plt.close()

    else :
        legend_list = list()
        for vals in Input :
            try :
                if vals != 'total'  :
                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]),linewidth=0.75)
                    print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                    print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
                    legend_list.append(vals)
            except :
                print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue

        if len(legend_list)>0 :
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title}')
            plt.xlabel(time_units.capitalize())
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname,bbox_inches = 'tight')
            print(f'\nFigure {fname} produced and saved.\n')
            plt.close()


def output_reader(filename, NOI, time_units = 'days'):
    """
    Austin Czyzewski's function to read values from ORIGEN .out files
    The workflow of this function goes something like this:
        - Import a file as one large string
        - Seperate string into Cases in .out file
        - Create a dataframe from the actual cases themselves
            - Get rid of the information we already know that surrounds the data
            - Split each case into its three parts: Light Elements, Fission Products, and Actinides
            - Use temporary dataframes that will constantly be overwritten to not destroy our PC
        - Append each case to an overall dataframe for each isotope source type (AC, LE, FP)
        - Add the index in as a Time column in the dataframe for plotting
        - Use pandas built in method to convert from strings to floats
    """
    ###################################
    ### Import the file as a string ###
    ###################################
    with open(filename, 'r') as file:
        first_file_string = file.read()#.replace('\n', '')
        file.close()
        
    first_file_string = re.sub(r'(\d{1}.\d{4})(-\d{3})', r'\1E\2', first_file_string)
#     #The above searches for "#.####-###" and replaces them with "#.####E-###"
    Case_Intervals = re.findall(r't\s*=\s*\[[^\]]*\]|time\s*=\s*\[[^\]]*\]', first_file_string)
#     #This regex searches for the times that each case runs for. The amount gathered here will be used later
        #To verify all cases are present in the output files.
    
    Integer_Interval_List = list()
    Case_Start_List = list()
    Case_End_List = list()
    for Interval in Case_Intervals:
        if 'i' in Interval:

            Interval_String = re.split('\[|i\s+',Interval) #This detects the number before i, the amount of timesteps in the interval
            Integer_Interval_List.append(int(Interval_String[1]))
            Case_times = re.split('\s{1,}|\]',Interval_String[2])

            Case_Start_List.append(float(Case_times[0])) #this is the start time. Most often zero
            Case_End_List.append(float(Case_times[1])) #End time. The useful bit



    print("{} Cases in {}".format(len(Integer_Interval_List), filename))
    
    
    ###################################
    # Split them using key phrase, "in curies for case {decay/irrad}"
    ###################################
    groups = re.split(r'in\ curies\ for\ case\ \Sirrad\S|in\ curies\ for\ case\ \Sdecay\S', \
                      first_file_string, flags=re.MULTILINE)
    
    groups = groups[1:]
    # The first group is all of the junk before the first actual table. Just dump it
    if len(Integer_Interval_List) != len(groups):
        print("#"*120 + "\nWARNING: \nDetected number of case time intervals does not match the amount of tables found."\
              "\nPlease ensure the proper print statement is present in all cases in the input file."\
             "\nIf all cases are present, one case may not have printed properly, please rerun the ORIGEN input file and check again.\n" + "#"*120)

    all_times = list()
    header_unit_list = list()
    Start_End_Times = list()

    All_LE = pd.Series(dtype = object)
    All_AC = pd.Series(dtype = object)
    All_FP = pd.Series(dtype = object)
    
    print("Creating DataFrames")
    for number, case in enumerate(groups):
        print("Case ({}/{})\r".format(number+1,len(groups)), end = '')
        
        # Handle the last table from each split section
        #################################
        data_from_case = re.sub(r'\s{2,}(?=\d+)',"  ", case)
        data_from_case = re.sub(r'^[.]\s*|^\s{2}',"", data_from_case, flags = re.MULTILINE)
        data_from_case = re.split(r'he-3', data_from_case)
        
        header_unit_string = re.findall('\d{1,}[a-z]{1,2}\s{2}',data_from_case[0], flags = re.MULTILINE)
        header_unit = re.findall('[a-z]{2}|[a-z]{1}', header_unit_string[1])[0]
        header_unit_list.append(header_unit)

        header_handling = re.split(r"{}(.+)".format(header_unit),data_from_case[0], flags = re.MULTILINE)

        times = header_handling[1].split('{}'.format(header_unit))
        
        start_time = times[1] 
        times.insert(1,start_time)
        Start_End_Times.append((float(times[0]),float(times[-2])))
        
        cut_number = 0
        if (number == 0):# or (number == len(groups)-1):
            cut_number = -1
        else:
            cut_number = -2
            
        if time_units == 'years':
            times = np.array(times[:cut_number]).astype(float)/365.25 #The first and last objects are empty strings
        else:
            times = np.array(times[:cut_number]).astype(float)
            
        all_times.append(times)
        
        temp_data = header_handling[2].split('\n') 
        
        #t_df is short for temporary DataFrame. I abbreviate to make it a little bit easier to read
        
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df = t_df.transpose() # We will be transposing all of our dataframes.
                    # We want to build on times Not on isotopes.
        header = t_df.iloc[0] #The first row in this dataframe is the isotope names we want
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head) #Get rid of the dash in the isotope names

        ##################################################################################################################
        
        temp_data = data_from_case[1].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
#         t_df.iloc[0] = t_df.iloc[0].shift(1)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
            
        header = pd.concat([pd.Series(["he3"]),header[1:]]) #Adding he3 as the name back to its respective isotope
        
        #Here we create a mask in order to name columns and index easier (maybe not easier but I like it this way)
#         df_naming_mask = t_df[2:]
        if (number == 0):# or (number == len(groups) - 1):
#             print("-"*80)
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
            
        df_naming_mask.columns = header #Name the columns by their isotope partner's name
        LE_df_final = df_naming_mask.set_index(times).iloc[1:]


        ##################################################################################################################
        #See above for what we're doing here
        temp_data = data_from_case[2].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
                
                
        header = pd.concat([pd.Series(["he3"]),header[1:]])
        if (number == 0):# or (number == len(groups) - 1):
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
        df_naming_mask.columns = header
        AC_df_final = df_naming_mask.set_index(times).iloc[1:]
#         print(times)
        ##################################################################################################################
        # Handle the last table from each split section
        FP_handling = re.split(r"\-{6,}",data_from_case[3]) #Gets rid of everything after the actual .out file
        
        #Back to what we've seen before (if you've been paying attention ;)
        temp_data = FP_handling[0].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df.iloc[0] = t_df.iloc[0].shift(1)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
        header = pd.concat([pd.Series(["he3"]),header[1:]])
        if (number == 0):# or (number == len(groups) - 1):
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
        df_naming_mask.columns = header
        
        
        FP_df_final = df_naming_mask.set_index(times).iloc[1:] #This is very close to doing what I want
        
        ##################################################################################################################
        ###################################
        # Append the new data to the big dataframe with each data type
        ###################################
        All_LE = pd.concat([All_LE,LE_df_final],sort = True)
        All_AC = pd.concat([All_AC,AC_df_final],sort = True)
        All_FP = pd.concat([All_FP,FP_df_final],sort = True)
        
        if (len(All_LE) == 0) or (len(All_AC) == 0) or (len(All_FP) == 0):
            print("#"*120 + "\nWARNING: \nDetected length of tables is 0.\nThis problem may occur if there are no print statements in the input file."\
                  "\nPlease ensure the proper print statement is present in all cases in the input file."\
                 "\nThe format for the print statement is as follows and should precede the save statement in each case:\n"\
                  "print{\n        nuc{ units=CURIES }\n        cutoffs[ ALL = 0 ]\n    }\n" + "#"*120)
            input("Please press enter to acknowledge this statement and close the script.")
            exit()

    print("All cases stored in DataFrames as strings")
    

    global Times_list
    Times_list = list()   #[Start_End_Times[0][0]]
    #print(Start_End_Times)

    Starts = 0
    Ends = 0
    for Interval, Start, End in zip(Integer_Interval_List, Case_Start_List,Case_End_List):
        Ends += Start + End
        Calculated_Times = np.linspace(Starts,Ends,2+Interval)[:-1]
        Starts += End

        for time in Calculated_Times:
            Times_list.append(time)

    Times_list.append(Ends)
    if time_units == 'years' :
        for num, time in enumerate(Times_list):
            Times_list[num] = time/365.25
    
    #Here, NOI is to identify the Type of isotope of interest
    if NOI == 'FP':
        All_FP = All_FP.drop([0,''], axis = 1)
        All_FP.index = pd.Series(Times_list)#, downcast="float")
        print("Converting strings to floats in DataFrame. This could take some time")
        
        for column in All_FP:
            All_FP[All_FP[column].name] = pd.to_numeric(All_FP[All_FP[column].name])
        
        print("String conversion complete\n")
        
        All_FP.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        return All_FP
    
    
    if NOI == 'AC':
        All_AC = All_AC.drop([0,''], axis = 1)
        All_AC.index = pd.Series(Times_list)#, downcast="float")
        print("Converting strings to floats in DataFrame. This could take some time")
        
        for column in All_AC:
        #Converting strings to floats in DataFrame
            All_AC[All_AC[column].name] = pd.to_numeric(All_AC[All_AC[column].name])
            
        print("String conversion complete\n")
        
        All_AC.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        return All_AC
    

def dataframe_merger(List_of_DataFrames, time_units):
    """
    Here List_of_DataFrames, List_of_DataFrames[0] is intended to be LEU and 
        List_of_DataFrames[1] is intended to be NU
    """
#     print("Here are the time units: {}".format(time_units))
    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
            print('Computing U-237 activity as a function of time and adding it to the inventories.\n')
            List_of_DataFrames[1],List_of_DataFrames[0] = U_237_adder(List_of_DataFrames[1],List_of_DataFrames[0], time_units = time_units)
            
    if Portion_of_core == 1:

        Reset_Index_LEU = List_of_DataFrames[0].drop(columns = ["Time ({})".format(time_units)])
        Reset_Index_LEU["Total_Activity"] = Reset_Index_LEU.iloc[:, 1:].sum(axis=1)
        Reset_Index_LEU = Reset_Index_LEU.sort_values(by = Reset_Index_LEU.iloc[-1].name, axis = 1, ascending = False)



        Reset_Index_NU = List_of_DataFrames[1].drop(columns = ["Time ({})".format(time_units)])
        Reset_Index_NU["Total_Activity"] = Reset_Index_NU.iloc[:, 1:].sum(axis=1)
        Reset_Index_NU = Reset_Index_NU.sort_values(by = Reset_Index_NU.iloc[-1].name, axis = 1, ascending = False)



        Reset_Index_LEU = Reset_Index_LEU.reset_index(drop = True)
        Reset_Index_NU = Reset_Index_NU.reset_index(drop = True)

        Total_Activity = Reset_Index_LEU.add(Reset_Index_NU, fill_value = 0)

        Total_Activity["Total_Activity"] = Total_Activity.iloc[:, 1:].sum(axis=1)
        Total_Activity = Total_Activity.sort_values(Total_Activity.iloc[-1].name, axis = 1, ascending = False)
    
        Total_Activity.index = pd.Series(Times_list)
        Reset_Index_LEU.index = pd.Series(Times_list)
        Reset_Index_NU.index = pd.Series(Times_list)
        Total_Activity.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        Reset_Index_LEU.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        Reset_Index_NU.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        time1 = time.time()
        print("Writing data to excel file...")
        print("Hang around, this may take a few minutes...")

        attempts_at_saving = 0
        while True:

            try:
                workbook = xlsxwriter.Workbook("Total_Core.xlsx")
                Total = workbook.add_worksheet("Total")
                LEU = workbook.add_worksheet("LEU")
                NU = workbook.add_worksheet("NU")

                worksheets = [Total, LEU, NU]
                dfs = [Total_Activity, Reset_Index_LEU, Reset_Index_NU]
                
                for iterative_value in range(3):
                    temporary_data_list = [list(dfs[iterative_value].columns)] + dfs[iterative_value].values.tolist()
                    for x, i in enumerate(temporary_data_list):
                        for y, _ in enumerate(i):
                            worksheets[iterative_value].write(x,y,temporary_data_list[x][y])
                    worksheets[iterative_value].freeze_panes(1,1)

                workbook.close()
                break
                
            except:
                print("Error Saving Total_Core.xlsx, please ensure all open copies are closed. Trying again in 15 seconds")
                attempts_at_saving += 1
                if attempts_at_saving >= 5:
                    break
                time.sleep(15)

        print("Total_Core.xlsx saved")
    if Portion_of_core == 2:
        Total_Activity = convert_to_1kgNU(List_of_DataFrames[1], time_units = time_units)
    return Total_Activity  
            
# def half_life_greater_than(isotope) :
#     with open('Half_Lives_List.txt','r') as file_handle :
#         bool = False
#         for line in file_handle :
#             if line.split()[0] == isotope:
#                 half_life = line.split()[3]

#                 # print(isotope, float(half_life) >= 86400*120.0)
#                 if float(half_life) >= 86400*120.0 :
#                     bool = True
#                     return True
#                 else :
#                     bool = True
#                     return False

#         if bool == False :
#             return False
#By the way, Chad, this next line doesn't do anything since return exits a function from running any further lines.
#             raise ValueError(f'Isotope {isotope} not found in half_lives_list.txt')
            
def half_life_greater_than(isotope) :
    global isotope_halflives
#     print("AAAAAAAAAAAAAAAAA",float(isotope_halflives[isotope]))
    try:
        half_life = float(isotope_halflives[isotope])
        if half_life >= 86400*120.0:
            return True
        else:
            return False
    except:
#         raise ValueError(f'Isotope {isotope} not found in half_lives_list.txt')
        return False


def split_120(original) :


    Greater_than = pd.DataFrame()
    Less_than = pd.DataFrame()

    isotopes = list(original)
#     time_identifier = f'Time ({time_units})'

    for isotope in isotopes :


#         if isotope == 'Totals' or isotope == 'Subtotals':
        if isotope == 'Total_Activity' or isotope == f'Time ({time_units})':

            continue

#         elif isotope != time_identifier :
#         print(number, isotope)
        if half_life_greater_than(isotope) :
            Greater_than.insert(0,isotope,original[isotope])
        else :
            Less_than.insert(0,isotope,original[isotope])

#         else :
#             pass
#             #raise ValueError(f'Isotope {isotope} passed if tests.\n')


    total_list = list()

    for key,value in Greater_than.iterrows() :
        sum = 0.0
        for vals in value :
            sum += vals
        total_list.append(sum)
    Greater_than.insert(0,'Total',total_list)

    total_list = list()

    for key,value in Less_than.iterrows() :
        sum = 0.0
        for vals in value :
            sum += vals
        total_list.append(sum)
    Less_than.insert(0,'Total',total_list)

    return Greater_than, Less_than
print('The Inventory Plotter: Author: Chad Denbrock, Co-Author: Austin Czyzewski, Niowave Inc. August 2020; revised February 2021\n\n')
print(f'This script makes the following assumptions in regard to how the ORIGEN simulations are run:'\
     f'The units in the input file are in DAYS. Other units will either crash the program or output invalid data.\n'\
     f'There is a print statement for every case ran in the file. In this print statement, the units must be specified to '\
     f'be CURIES and the CUTOFFS for ALL element tables must be set to 0.\n'\
      f'The output files are in the directory that this Python script is run. There must be one LEU and one NU output file.\n')

while True :
    time_units = input('What time units do you want the excel and plots to have? (e.g. Days or Years)\n')
    time_units = time_units.lower()
#    if time_units.lower() == 'years' :
    if time_units == 'years':
        break
#    elif time_units.lower() == 'days' :
    elif time_units == 'days':
        break
    else :
        print('The time units must be either days or years. Try again.\n')

#       Plotting fission products or actinides?
while True :
    kind_of_isotopes = input('What are you plotting? (Fission Products = FP or Actinides = An)\n')
    if kind_of_isotopes.lower() == 'fission products' or kind_of_isotopes.lower() == 'fp' :
        Title = 'Fission Products'
        fname = 'Fission-Products_UTA-2'
        plotting_type = "FP"
        break
    elif kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an':
        Title = 'Actinides'
        fname = 'Actinides_UTA-2'
        plotting_type = "AC"
        break
    else :
        print('You must be plotting either Actinides or fission products, not both or neither.')
        
while True :
    Portion_of_core = int(input('What portion of the core would you like to analyze (1 or 2)? \n'\
                                '1: Whole Core (LEU + NU)\n'\
                                '2: Dispersable (Hottest 1 kgNU)\n'))
    if Portion_of_core == 1:
        Title = Title + ' in the Whole Core'
        fname = fname + '_whole_core'
        break
    elif Portion_of_core == 2:
        Title = Title + ' in the hottest 1 kgNU'
        fname = fname + '_hottest_1kgNU'
        break
    else :
        print('Type 1 or 2 as your selection for what part of the core you would like to analyze.\n')

files = glob.glob("*.out")
LEU_files = glob.glob("*LEU*.out")
NU_files = glob.glob("*NU*.out")
#print(LEU_files, NU_files)
print("#"*60)
print("---LEU---")
print("#"*60)
attempts = 0
while True:
    try:
        if len(LEU_files) == 1:
            LEU_file = LEU_files[0]
        else:
            print("Please select which output file to analyze (LEU)")
            for number,file in enumerate(LEU_files):
                print("{}: {}\n".format(number, file))
            file_number_LEU = int(input(""))
            LEU_file = LEU_files[file_number_LEU]
    #         print("Loading {}".format(files[file_number_LEU]))
        print("{} Selected".format(LEU_file))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        attempts += 1
        if attempts > 5:
            exit()
        continue


print("#"*60)
print("---NU---")
print("#"*60)
while True:
    try:
        if len(NU_files) == 1:
            NU_file = NU_files[0]
        else:
            print("Please select which output file to analyze (NU)")
            for number,file in enumerate(NU_files):
                print("{}: {}\n".format(number, file))
            file_number_NU = int(input(""))
            NU_file = NU_files[file_number_NU]
    #         print("Loading {}".format(files[file_number_LEU]))
        print("{} Selected\n\n".format(NU_file))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        continue
        
#Run it
###############################################################################
LEU = output_reader(LEU_file, plotting_type, time_units = time_units.lower())
NU = output_reader(NU_file, plotting_type, time_units = time_units.lower())
dfs = dataframe_merger([LEU, NU], time_units = time_units.lower())
The_Inventory = dfs

while True:
    try:
        plotting(The_Inventory)
    except:
        print("Error raised in plotting, please make sure plots are closed")
    end = input("Did this produce the plots that you desired? (Y/N)  ")
    if (end.lower() == "y") or (end.lower() == "yes"):
        break
    elif end.lower() == 'no' or end.lower() == 'n':
        print("\nPlease try again\n")
        print("Input list has been reset, please type all desired elements again.\n")
        continue
    else:
        print("Input not understood, please try again. (Yes, No, Y, N, (not case sensitive) are accepted)")
        print("Input list has been reset, please type all desired elements again.\n")
        continue
        
print("\n" + "-"*60 + "\nInventory Plotter Complete\n" + "-"*60)
input("Please Press 'Enter' to close this script")
