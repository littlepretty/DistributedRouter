#!/usr/bin/Gnuplot

# Gnuplot script file for plotting data in file "progress.dat"
set   autoscale                        # scale axes automatically
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set xtic auto                          # set xtics automatically
set ytic auto                          # set ytics automatically
set title "Discovery Metric as Function of Iteration"
set xlabel "#Iteration"
set ylabel "Discovery Progress (%)"
#set key 0.01,100
#set label "Yield Point" at 0.003,260
#set arrow from 0.0028,250 to 0.003,280
set xr [0.0 : 8.0]
set yr [0.0 : 105.0]
set terminal postscript portrait enhanced mono dashed lw 1 "Helvetica" 14
set output "progress.ps"
plot "progress.dat" using 1:2 title 'R1' with linespoints lt 1 pt 1, \
     "progress.dat" using 1:3 title 'R6' with linespoints lt 3 pt 3
