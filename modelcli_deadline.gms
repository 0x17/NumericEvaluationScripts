$ontext
example parameters: --instname=QBWLBeispiel.sm --iterlim=99999 --timelimit=99999 --solver=CPLEX --trace=0 --nthreads=1

STj=tk bzw. FTj=tk bedeutet, dass AG j am Ende von Periode k anf�ngt bzw. beginnt.
tk als Zeitpunkt interpretiert bedeutet also Ende der Periode k.
$offtext

$eolcom �

*$set instname ProjectStructureData

options OPTCR = 0
        MIP = %solver%
        RESLIM = %timelimit%
        THREADS = %nthreads%
        ITERLIM = %iterlim%;

sets j Arbeitsg�nge
     t Perioden
     r Ressourcen;

alias(j,i);
alias(t,tau);

sets pred(i,j) yes gdw. i Vorg�nger von j ist
     tw(j, t) yes gdw. t im Zeitfenster von j liegt
     actual(j) yes gdw. Job kein Dummy
     lastJob(j) yes gdw. Job letzter AG
     fw(j, t, tau) yes gdw. AG j in tau beendet werden kann wenn er in t lief;

parameters
         seedsol(j)      Startloesung
         solvetime       CPU-Zeit
         slvstat         Termination status
         modelstat       Model solution status
         zmax(r)         Maximale ZK
         kappa(r)        Kosten pro Einheit ZK
         capacities(r)   Kapazit�ten
         durations(j)    Dauern
         u(t)            Erl�s (Parabel) bei Makespan t
         efts(j)         Fr�heste Startzeitpunkte
         lfts(j)         Sp�teste Endzeitpunkte
         demands(j,r)    Bedarf;

binary variable  x(j,t) 1 gdw. AG j in Periode t endet d.h. FTj=t;
variables        z(r,t) Einheiten ZK von r in Periode t gebucht
                 profit Gewinn (Parabel)
                 ms Makespan;

scalar deadline;

equations
                objective   Weitere ZF
                precedence  Vorrangbeziehung durchsetzen
                resusage    Ressourcenverbrauchsrestriktion
                once        Jeden AG genau 1x einplanen
                oclimits    Beschr�nke buchbare ZK
                shorterthandeadline Beschr�nkt Makespan
                objminms;

objective                 .. profit =e= sum(j$lastJob(j), sum(t$tw(j,t), x(j,t)*u(t)))-sum(r, sum(t, z(r,t)*kappa(r)));
objminms                  .. ms =e= sum(j$lastJob(j), sum(t$tw(j,t), x(j,t)*(ord(t)-1)));
precedence(i,j)$pred(i,j) .. sum(t$tw(i,t), (ord(t)-1)*x(i,t)) =l= sum(t$tw(j,t), (ord(t)-1)*x(j,t)) - durations(j);
resusage(r,t)             .. sum(j$actual(j), demands(j,r)*sum(tau$fw(j,t,tau), x(j,tau))) =l= capacities(r) + z(r,t);
once(j)                   .. sum(t$tw(j,t), x(j,t)) =e= 1;
oclimits(r,t)             .. z(r,t) =l= zmax(r);
shorterthandeadline       .. sum(j$lastJob(j), sum(t$tw(j,t), x(j,t)*(ord(t)-1))) =l= deadline;

model rcpspoc  /objective, precedence, resusage, once, shorterthandeadline/;
rcpspoc.optfile = %trace%;

model rcpsp /objminms, precedence, resusage, once/;

$GDXIN %instname%.gdx
$load j t r zmax kappa capacities durations u efts lfts demands pred seedsol
$GDXIN

tw(j, t)$(efts(j) <= (ord(t)-1) and (ord(t)-1) <= lfts(j)) = yes;
actual(j)$(1 < ord(j) and ord(j) < card(j)) = yes;
lastJob(j)$(ord(j) = card(j)) = yes;
fw(j, t, tau)$(ord(tau)>=ord(t) and ord(tau)<=ord(t)+durations(j)-1 and tw(j,tau)) = yes;
z.lo(r,t) = 0;
z.up(r,t) = zmax(r);
profit.lo = 0;

z.up(r,t) = 0;
solve rcpsp using mip minimizing ms;
scalar msNoOvertime;
msNoOvertime = ms.l;

z.up(r,t) = zmax(r);
solve rcpsp using mip minimizing ms;
scalar msMaxOvertime;
msMaxOvertime = ms.l;

execute_unload 'DebugOutput2.gdx';
*$exit

file fp /deadlineAndProfit.txt/;
put fp;
for(deadline = msMaxOvertime to msNoOvertime,
  x.up(j,t)$(lastJob(j) and ord(t)>deadline+1) = 0;
  x.up(j,t)$(not lastJob(j) or ord(t) <= deadline+1) = 1;
  solve rcpspoc using mip maximizing profit;
  solvetime = rcpspoc.resusd;
  slvstat = rcpspoc.solvestat;
  modelstat = rcpspoc.modelstat;
  if(modelstat = 1 and slvstat = 1, put deadline ';':1 ms.l ';':1 round(profit.l,6):<99:4 /; else);
  execute_unload 'DebugOutput.gdx';
);
putclose fp;

*$ontext
*execute_unload '%instname%_results.gdx' x.l x.m z.l z.m profit.l profit.m solvetime slvstat modelstat;
*display z.l;

$ontext
file fp /%outpath%myschedule.txt/;
put fp;
scalar stj;
loop(j,
  loop(t$tw(j,t),
    if(x.l(j,t)=1,
      stj = ord(t) - durations(j) - 1;
      put ord(j):>4:0 '->':2 stj:<4:0 / )));
putclose fp;

file fpprof /%outpath%myprofit.txt/;
put fpprof;
put profit.l;
putclose fpprof;
$offtext

$ontext
*file fpres /%outpath%_GMS_%solver%_Results.txt/;
file fpres /GMS_%solver%_Results.txt/;
fpres.ap = 1;
put fpres;
if(modelstat = 1 and slvstat = 1,
  put '%instname%' ';':1 round(profit.l,4):<99:4 /;
else);
putclose fpres
$offtext
