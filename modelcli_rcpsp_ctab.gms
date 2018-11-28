$ontext
Beispielhafter Aufruf für QBWLBeispiel.sm.gdx:
gams modelcli.gms --instname=QBWLBeispiel.sm

STj=tk bzw. FTj=tk bedeutet, dass AG j am Ende von Periode k anfängt bzw. beginnt.
tk als Zeitpunkt interpretiert bedeutet also Ende der Periode k.
$offtext

*$set instname ProjectStructureData

options OPTCR = 0
        MIP = GUROBI
        RESLIM = 36000
        THREADS = 1
        ITERLIM = 2000000000;

sets j Arbeitsgänge
     t Perioden
     r Ressourcen
     l Ressourceneinheiten;

alias(j,i);
alias(j,k);
alias(t,tau);

sets pred(i,j) yes gdw. i Vorgänger von j ist
     tw(j, t) yes gdw. t im Zeitfenster von j liegt
     actual(j) yes gdw. Job kein Dummy
     lastJob(j) yes gdw. Job letzter AG
     fw(j, t, tau) yes gdw. AG j in tau beendet werden kann wenn er in t lief
     notclosure(i,j)
     predTransClosure(i,j)
     forbiddenPairs(i,j)
     forbiddenTriplets(i,j,k);

parameters
         capacities(r)   Kapazitäten
         durations(j)    Dauern
         efts(j)         Früheste Startzeitpunkte
         lfts(j)         Späteste Endzeitpunkte
         demands(j,r)    Bedarf;

binary variables  y(i,j) 1 gdw. AG j direkt nach AG i eine Ressource nutzt
                  v(j,l,r) 1 gdw. AG j auf Einheit l von Ressource r;

variables       s(j)     Startzeitpunkt von AG j
                makespan Projektdauer;

equations
                objective   ZF
                cap
                precedence  Vorrangbeziehung durchsetzen
                sync1
                sync2
                fpairsorder
                ftripletsorder;

objective .. makespan =e= sum(j$lastJob(j), s(j));
cap(j,r) .. sum(l$(ord(l)<=capacities(r)), v(j,l,r)) =e= demands(j,r);
precedence(i,j)$pred(i,j) .. s(i)+durations(i) =l= s(j);
sync1(i,j,r,l)$(notclosure(i,j) and ord(i)<ord(j)) .. v(i,l,r) + v(j,l,r) =l= 1 + y(i,j) + y(j,i);
sync2(i,j)$notclosure(i,j) .. s(i) + durations(i) =l= s(j) + lfts(i) * (1-y(i,j));

**************************************************
* performance enhancement no. 1 from CTAB paper
fpairsorder(i,j)$forbiddenPairs(i,j) .. y(i,j)+y(j,i) =e= 1;
ftripletsorder(i,j,k)$forbiddenTriplets(i,j,k) .. y(i,j)+y(j,i)+y(i,k)+y(k,i)+y(j,k)+y(k,j) =g= 1;
**************************************************

model rcpspoc /all/;

$GDXIN %instname%.gdx
$load j t r l capacities durations efts lfts demands pred predTransClosure forbiddenPairs forbiddenTriplets
$GDXIN

actual(j)$(1 < ord(j) and ord(j) < card(j)) = yes;
lastJob(j)$(ord(j) = card(j)) = yes;

tw(j, t)$(efts(j) <= (ord(t)-1) and (ord(t)-1) <= lfts(j)) = yes;
fw(j, t, tau)$(ord(tau)>=ord(t) and ord(tau)<=ord(t)+durations(j)-1 and tw(j,tau)) = yes;

notclosure(i,j)$(not predTransClosure(i,j)) = yes;

makespan.lo = 0;
s.lo(j) = efts(j)-durations(j);
s.up(j) = lfts(j)-durations(j);
v.up(j,l,r)$(ord(l) > capacities(r)) = 0;

**************************************************
* performance enhancement no. 2 from CTAB paper
*$ontext
parameters maxDemandJobs(r);
scalar maxDemand;
loop(r,
  maxDemand = 0;
  loop(j,
    if(demands(j,r) > maxDemand,
      maxDemand = demands(j,r);
      maxDemandJobs(r) = ord(j);
    );
  );
);
loop(r,
  loop(j$(ord(j)=maxDemandJobs(r)),
    loop(l$(ord(l) <= demands(j,r)),
      v.lo(j,l,r) = 1;
      v.up(j,l,r) = 1;
    );
  );
);
*$offtext
**************************************************

solve rcpspoc using mip minimizing makespan;

scalars solvetime, solvestat, modelstat;
solvetime = rcpspoc.resusd;
solvestat = rcpspoc.solvestat;
modelstat = rcpspoc.modelstat;

execute_unload '%instname%_results.gdx' s.l s.m makespan.l makespan.m solvetime solvestat modelstat;

file fpres /GMS_GUROBI_CTAB_Results.txt/;
fpres.ap = 1;
put fpres;
if(modelstat = 1 and solvestat = 1,
  put '%instname%' round(makespan.l,6)::6 solvetime;
else
  put '%instname%' 'infes';
);
putclose fpres
