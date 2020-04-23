## 181213 only removed some parentheses from print statements, otherwise
## same as 181126 version
## 181214 put all parentheses back in because in Python 3 print is a function
## 190108 not ideal but using this file as a data repository for the 3-gap 2-pass system; adding tuning data for test that starts today
## 191112 included k values for both working triple gaps

import numpy as np
#import scipy as sp
#import scipy.integrate as intgr
import matplotlib.pyplot as plt
import array
import time


def S1(f1, f2, f3, k1, k2):
    return [(1 + k1)/f1**2 , -k1 / f1**2, 0] , [-k1 / f2**2, (1 + k1 + k2)/f2**2 , -k2 / f2**2], [0, -k2 / f3**2, (1 + k2) / f3**2]

def che1(f1, f2, f3, k1, k2):
    valuesandmatrix = np.linalg.eig(S1(f1, f2, f3, k1, k2))
    return valuesandmatrix[0]

def FM1(f1, f2, f3, k1, k2):
    eigenvalues = che1(f1, f2, f3, k1, k2)
    resultmodes = np.array([1/(np.sqrt(eigenvalues[0])),1/(np.sqrt(eigenvalues[1])),1/(np.sqrt(eigenvalues[2]))])
    return resultmodes

def J1(f1, f2, f3, k1, k2):
    m = 2
    testarray = S1(f1, f2, f3, k1, k2)
    norm = max(abs(np.linalg.eig(testarray)[1][0][m]) , abs(np.linalg.eig(testarray)[1][1][m]) , abs(np.linalg.eig(testarray)[1][2][m]))
    return np.array([abs(np.linalg.eig(testarray)[1][0][m]) / norm , abs(np.linalg.eig(testarray)[1][1][m]) / norm , abs(np.linalg.eig(testarray)[1][2][m]) / norm])

def J2(f1, f2, f3, k1, k2):
    m = 1
    testarray = S1(f1, f2, f3, k1, k2)
    norm = max(abs(np.linalg.eig(testarray)[1][0][m]) , abs(np.linalg.eig(testarray)[1][1][m]) , abs(np.linalg.eig(testarray)[1][2][m]))
    return np.array([abs(np.linalg.eig(testarray)[1][0][m]) / norm , abs(np.linalg.eig(testarray)[1][1][m]) / norm , abs(np.linalg.eig(testarray)[1][2][m]) / norm])

def J3(f1, f2, f3, k1, k2):
    m = 0
    testarray = S1(f1, f2, f3, k1, k2)
    norm = max(abs(np.linalg.eig(testarray)[1][0][m]) , abs(np.linalg.eig(testarray)[1][1][m]) , abs(np.linalg.eig(testarray)[1][2][m]))
    return np.array([abs(np.linalg.eig(testarray)[1][0][m]) / norm , abs(np.linalg.eig(testarray)[1][1][m]) / norm , abs(np.linalg.eig(testarray)[1][2][m]) / norm])

## 200331 12:34 East Tunnel (cavity T 5.2 K, tuner pulled ~three turns) 81%
measuredmodes = [351.4333, 350.4844 , 350.0615]

#### 200331 12:34 East Tunnel (cavity T 5.4 K, tuner pulled ~three turns) 81%
##measuredmodes = [351.4325, 350.4824 , 350.0601]

#### 200331 12:15 East Tunnel (cavity T 5.6 K, tuner pulled one turn)
##measuredmodes = [351.2445, 349.8050 , 349.5038]

#### 200331 12:06 East Tunnel (cavity T 6 K, tuner pulled half turn)
##measuredmodes = [351.2038, 349.6132 , 349.3200]

#### 200331 11:19 East Tunnel (T middle 7.5 K, tuner loose) 61%
##measuredmodes = [351.165, 349.410 , 349.145]

#### 200331 11:19 East Tunnel (T middle 78 K, tuner loose)
##measuredmodes = [350.411, 349.319 , 349.065]

#### 200331 10:54 East Tunnel (T middle 135 K, tuner loose)
##measuredmodes = [350.429, 349.215 , 348.990]

#### 200331 10:18 East Tunnel (T middle 246 K, tuner loose)
##measuredmodes = [350.404, 349.084 , 348.865]

#### 191112 (cold, stretched just over two turns)
##measuredmodes = [351.557, 350.852 , 350.118]

#### 180605 (from log book)
##measuredmodes = [351.480, 350.770 , 350.076]

#### 190108 1237 (cavity at 5 K, tuner stretched 3 turns)
##measuredmodes = [351.448, 350.456 , 350.050]

#### 190108 1230 (cavity at 5 K, tuner stretched 2.5 turns)
##measuredmodes = [351.397, 350.294 , 349.933]

#### 190108 1156 (cavity at 5 K, tuner stretched 2 turns)
##measuredmodes = [351.355, 350.133 , 349.810]

#### 190108 1152 (cavity at 5 K, tuner stretched 1.5 turns)
##measuredmodes = [351.318, 349.971 , 349.676]

#### 190108 1145 (cavity superconducting tuner loose cavity at ~5 K)
##measuredmodes = [351.214, 349.466 , 349.229]

#### 190108 1110 (tuner unlocked cavity at ~40 K)
##measuredmodes = [351.188, 349.430 , 349.190]

#### 190108 1045 (tuner unlocked cavity at ~90 K)
##measuredmodes = [351.149, 349.360 , 349.136]

#### 190108 1000 (tuner unlocked cavity at ~200 K)
##measuredmodes = [350.998, 349.197 , 348.996]

## not using amplitude fitting so just always define unity matrices
measuredpimodeamplitude = [1 , 1 , 1]
measured2pi3modeamplitude = [1 , 1 , 1]
measuredpi3modeamplitude = [1 , 1 , 1]


## k values for east tunnel triple gap (as of Nov. 2019)
kmodel = np.array([2.607e-3, 2.4160e-3])

## k values for west tunnel triple gap (as of Nov. 2019)
##kmodel = np.array([2.424e-3, 2.321e-3])

ksearch = 0
print ('measured modes')
print (measuredmodes)
print ('measured amplitudes')
print (measuredpimodeamplitude)
print (measured2pi3modeamplitude)
print (measuredpi3modeamplitude)

kmodelmax = 5e-3

## setup initial guesses for cell frequencies

fcell = [ 351.0,  351.9,   350.8] ## MHz
print ('initial cell frequencies')
print (fcell)

## do initial calcuation

modelmodes = FM1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
errormodes = modelmodes - measuredmodes
kmodelpiamp = J1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
piamperror = np.linalg.norm(kmodelpiamp - measuredpimodeamplitude)
kmodel2pi3amp = J2(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
tpi3amperror = np.linalg.norm(kmodel2pi3amp - measured2pi3modeamplitude)
kmodelpi3amp = J3(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
pi3amperror = np.linalg.norm(kmodelpi3amp - measuredpi3modeamplitude)
amperror = piamperror + pi3amperror + tpi3amperror

print ('initial amplitudes')
print ('pi mode')
print (J1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1]))
print ('2pi/3 mode')
print (J2(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1]))
print ('pi/3 mode')
print (J3(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1]))
 
print ('initial modes from guess for cells')
print (modelmodes)

print ('initial frequency error')
error = np.linalg.norm(errormodes)
print (errormodes, error)
if ksearch==1:
    print ('initial amplitude error')
    print ('pi mode')
    print (kmodelpiamp - measuredpimodeamplitude, np.linalg.norm(piamperror))
    print ('2pi/3 mode')
    print (kmodel2pi3amp - measured2pi3modeamplitude, np.linalg.norm(tpi3amperror))
    print ('pi/3 mode')
    print (kmodelpi3amp - measuredpi3modeamplitude, np.linalg.norm(pi3amperror))
    print ('sum')
    print (amperror)


    ## find solution

    ## initialization
desiredfrequencyerror = 1e-5
desiredamplitudeerror = 1e-2
amplitudeerror = 1
## just to make sure we don't cycle because we aren't adjusting k
if ksearch == 0: desiredamplitudeerror = 1e6
## error = 1
report = 0
reportperiod = 15000
progresscheck = 100000
noprogress = 0
maxnoprogressthisreport = 0

while ((error > desiredfrequencyerror or amperror > desiredamplitudeerror) and noprogress < progresscheck):
    
    report = report +1
    if report > reportperiod:
        print ('mode frequencies at', modelmodes)
        print ('cell frequencies at', fcell)
        error = np.linalg.norm(errormodes)
        if ksearch==1:
            print ('k at', kmodel)
        print ('---------------------------')
        print ('mode frequencies error is', error)
        if ksearch==1:
            print ('amplitude error is', amperror)
        print ('pi mode amplitudes are ' , J1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1]))
        print ('---------------------------')
        print ('                                   maximum tries with no better solution this report is', maxnoprogressthisreport)
        print ('---------------------------')
        report = 0
        maxnoprogressthisreport = 0
    if error < 0.5:
        mutation = error
    else:
        mutation = 0.5
    fcelldaughter1 = fcell + (-mutation/2 + mutation * np.random.rand(3))
    ##print ('new daughter 1')
    ##print (fcelldaughter1)
    daughter1modes = FM1(fcelldaughter1[0], fcelldaughter1[1], fcelldaughter1[2], kmodel[0], kmodel[1])
    ##print ('new daughter 1 modes')
    ##print (daughter1modes)
    ##print ('new daughter 1 error')
    daughter1error = daughter1modes - measuredmodes
    ##print (daughter1error, np.linalg.norm(daughter1error))
    if (np.linalg.norm(daughter1error) < error):
        
        fcell = fcelldaughter1
        modelmodes = daughter1modes
        errormodes = daughter1error

        kmodelpiamp = J1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
        kmodel2pi3amp = J2(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
        kmodelpi3amp = J3(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
        
        piamperror = abs(np.linalg.norm(kmodelpiamp - measuredpimodeamplitude))
        pi3amperror = abs(np.linalg.norm(kmodelpi3amp - measuredpi3modeamplitude))
        tpi3amperror = abs(np.linalg.norm(kmodel2pi3amp - measured2pi3modeamplitude))
        amperror = piamperror + pi3amperror + tpi3amperror
        
        noprogress = 0
    else:
        noprogress = noprogress + 1
         
    if amperror < 0.0005:
        kmutation = amperror / 50
    else:
        kmutation = amperror / 1e7

    if ksearch == 1:
        newkmodel = abs(kmodel + (-kmutation/2 + kmutation * np.random.rand(2)))
        newkmodelpiamp = J1(fcell[0], fcell[1], fcell[2], newkmodel[0], newkmodel[1])
        newkmodel2pi3amp = J2(fcell[0], fcell[1], fcell[2], newkmodel[0], newkmodel[1])
        newkmodelpi3amp = J3(fcell[0], fcell[1], fcell[2], newkmodel[0], newkmodel[1])
        newkpiamperror = np.linalg.norm(newkmodelpiamp - measuredpimodeamplitude)
        newk2pi3amperror = np.linalg.norm(newkmodelpi3amp - measuredpi3modeamplitude)
        newkpi3amperror = np.linalg.norm(newkmodel2pi3amp - measured2pi3modeamplitude)
        newkerror = newkpiamperror + newkpi3amperror + newk2pi3amperror
        if (newkmodel[0] < kmodelmax and newkmodel[1] < kmodelmax and newkerror < amperror):
            kmodel = newkmodel
            kmodelpiamp = J1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
            kmodel2pi3amp = J2(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
            kmodelpi3amp = J3(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
            
            piamperror = abs(np.linalg.norm(kmodelpiamp - measuredpimodeamplitude))
            pi3amperror = abs(np.linalg.norm(kmodelpi3amp - measuredpi3modeamplitude))
            tpi3amperror = abs(np.linalg.norm(kmodel2pi3amp - measured2pi3modeamplitude))
            amperror = piamperror + pi3amperror + tpi3amperror

            modelmodes = FM1(fcell[0], fcell[1], fcell[2], kmodel[0], kmodel[1])
            errormodes = modelmodes - measuredmodes
            noprogress = 0

    noprogress = noprogress + 1
    if noprogress > maxnoprogressthisreport: maxnoprogressthisreport = noprogress

    
                    
print ('result for cell frequencies')
print (fcell)
print ('result for mode frequencies')
print (modelmodes)
print ('error in frequencies')
print (errormodes, error)
if ksearch==1:
    print ('result for coupling k')
    print (kmodel)
    print ('error in mode amplitudes')
    print (amperror)
print ('amplitudes for pi mode')
print (J1(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1]))
print ('amplitudes for 2 pi/3 mode')
print (J2(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1]))
print ('amplitudes for pi/3 mode')
print (J3(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1]))
print ('pi mode flatness as a percentage is ', (J1(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1])[0] + J1(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1])[1] + J1(fcell[0] , fcell[1] , fcell[2] , kmodel[0], kmodel[1])[2]) * 100 / 3, '%')
if error > desiredfrequencyerror:
    print ('**WARNING** cell frequencies did not converge')


