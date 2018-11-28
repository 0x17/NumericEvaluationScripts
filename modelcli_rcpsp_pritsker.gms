$ontext
Beispielhafter Aufruf für QBWLBeispiel.sm.gdx:
gams modelcli.gms --instname=QBWLBeispiel.sm

STj=tk bzw. FTj=tk bedeutet, dass AG j am Ende von Periode k anfängt bzw. beginnt.
tk als Zeitpunkt interpretiert bedeutet also Ende der Periode k.
$offtext

*$set instname ProjectStructureData

options OPTCR = 0
        MIP = %solver%
        RESLIM = %timelimit%
        THREADS = %nthreads%
        ITERLIM = %iterlim%;

sets j Arbeitsgänge
     t Perioden
     r Ressourcen;

alias(j,i);
alias(t,tau);

sets pred(i,j) yes gdw. i Vorgänger von j ist
     tw(j, t) yes gdw. t im Zeitfenster von j liegt
     actual(j) yes gdw. Job kein Dummy
     lastJob(j) yes gdw. Job letzter AG
     fw(j, t, tau) yes gdw. AG j in tau beendet werden kann wenn er in t lief;

parameters
         capacities(r)   Kapazitäten
         durations(j)    Dauern
         efts(j)         Früheste Startzeitpunkte
         lfts(j)         Späteste Endzeitpunkte
         demands(j,r)    Bedarf;

binary variable  x(j,t) 1 gdw. AG j in Periode t endet d.h. FTj=t;
variables        makespan Projektdauer;

equations
                objective   ZF
                precedence  Vorrangbeziehung durchsetzen
                resusage    Ressourcenverbrauchsrestriktion
                once        Jeden AG genau 1x einplanen;

objective                 .. makespan =e= sum(j$lastJob(j), sum(t$tw(j,t), x(j,t)*(ord(t)-1)));
precedence(i,j)$pred(i,j) .. sum(t$tw(i,t), (ord(t)-1)*x(i,t)) =l= sum(t$tw(j,t), (ord(t)-1)*x(j,t)) - durations(j);
resusage(r,t)             .. sum(j$actual(j), demands(j,r)*sum(tau$fw(j,t,tau), x(j,tau))) =l= capacities(r);
once(j)                   .. sum(t$tw(j,t), x(j,t)) =e= 1;

model rcpspoc  /objective, precedence, resusage, once/;

$GDXIN %instname%.gdx
$load j t r capacities durations efts lfts demands pred
$GDXIN

actual(j)$(1 < ord(j) and ord(j) < card(j)) = yes;
lastJob(j)$(ord(j) = card(j)) = yes;

tw(j, t)$(efts(j) <= (ord(t)-1) and (ord(t)-1) <= lfts(j)) = yes;
fw(j, t, tau)$(ord(tau)>=ord(t) and ord(tau)<=ord(t)+durations(j)-1 and tw(j,tau)) = yes;

makespan.lo = 0;

solve rcpspoc using mip minimizing makespan;

scalars solvetime, solvestat, modelstat;
solvetime = rcpspoc.resusd;
solvestat = rcpspoc.solvestat;
modelstat = rcpspoc.modelstat;

execute_unload '%instname%_results.gdx' x.l x.m makespan.l makespan.m solvetime solvestat modelstat;

file fpres /GMS_GUROBI_Pristker_Results.txt/;
fpres.ap = 1;
put fpres;
if(modelstat = 1 and solvestat = 1,
  put '%instname%' round(makespan.l,6)::6 solvetime;
else
  put '%instname%' 'infes';
);
putclose fpres
