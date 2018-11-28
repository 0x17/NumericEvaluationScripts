$ontext
Beispielhafter Aufruf für QBWLBeispiel.sm.gdx:
gams modelcli.gms --instname=QBWLBeispiel.sm

STj=tk bzw. FTj=tk bedeutet, dass AG j am Ende von Periode k anfängt bzw. beginnt.
tk als Zeitpunkt interpretiert bedeutet also Ende der Periode k.
$offtext

$eolcom §

*$set instname ProjectStructureData

options OPTCR = 0
        MIP = GUROBI
        RESLIM = 36000
        THREADS = 1
        ITERLIM = 2000000000;

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
         seedsol(j)      Startloesung
         solvetime       CPU-Zeit
         slvstat         Termination status
         modelstat       Model solution status
         zmax(r)         Maximale ZK
         kappa(r)        Kosten pro Einheit ZK
         capacities(r)   Kapazitäten
         durations(j)    Dauern
         u(t)            Erlös (Parabel) bei Makespan t
         efts(j)         Früheste Startzeitpunkte
         lfts(j)         Späteste Endzeitpunkte
         demands(j,r)    Bedarf;

binary variable  x(j,t) 1 gdw. AG j in Periode t endet d.h. FTj=t;
variables        z(r,t) Einheiten ZK von r in Periode t gebucht
                 profit Gewinn (Parabel);

equations
                objective   ZF
                precedence  Vorrangbeziehung durchsetzen
                resusage    Ressourcenverbrauchsrestriktion
                once        Jeden AG genau 1x einplanen;

objective                 .. profit =e= sum(j$lastJob(j), sum(t$tw(j,t), x(j,t)*u(t)))-sum(r, sum(t, z(r,t)*kappa(r)));
precedence(i,j)$pred(i,j) .. sum(t$tw(i,t), (ord(t)-1)*x(i,t)) =l= sum(t$tw(j,t), (ord(t)-1)*x(j,t)) - durations(j);
resusage(r,t)             .. sum(j$actual(j), demands(j,r)*sum(tau$fw(j,t,tau), x(j,tau))) =l= capacities(r) + z(r,t);
once(j)                   .. sum(t$tw(j,t), x(j,t)) =e= 1;

model rcpspoc  /objective, precedence, resusage, once/;

$GDXIN %instname%.gdx
$load j t r zmax kappa capacities durations u efts lfts demands pred seedsol
$GDXIN

actual(j)$(1 < ord(j) and ord(j) < card(j)) = yes;
lastJob(j)$(ord(j) = card(j)) = yes;

tw(j, t)$(efts(j) <= (ord(t)-1) and (ord(t)-1) <= lfts(j)) = yes;
fw(j, t, tau)$(ord(tau)>=ord(t) and ord(tau)<=ord(t)+durations(j)-1 and tw(j,tau)) = yes;

z.lo(r,t) = 0;
z.up(r,t) = zmax(r);
profit.lo = 0;

file fpres /SensitivityResults.txt/;
fpres.ap = 0;
fpres.nd = 2;
fpres.nr = 1;
fpres.nw = 4;
fpres.pw = 32767;
put fpres;
scalar cap_value, ndigits;
parameter sts(j) Startzeitpunkte;
ndigits=6;
put "cap_value;sts;solvetime" /;
for(cap_value = 3 to 6,
  capacities(r) = cap_value;
  solve rcpspoc using mip maximizing profit;
  solvetime = rcpspoc.resusd;
  slvstat = rcpspoc.solvestat;
  modelstat = rcpspoc.modelstat;
  if(modelstat = 1 and slvstat = 1,
    loop(j, loop(t$tw(j,t), if(x.l(j,t) = 1, sts(j)=ord(t)-durations(j)-1)));
    put cap_value:6:2 ';';
    loop(j, put sts(j):4:0 ';');
    put solvetime:6:2 /;
  else);
);

putclose fpres