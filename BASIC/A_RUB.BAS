10 DEFINT A-Z
20 CLS:C=7:RANDOMIZE TIMER
30 SCREEN 9,,0,0
40 DIM A(3,3),B(2,2),G(3,3),FX(11),FY(11)
50 GOSUB 510
60 DATA 120,125,220,125,120,225,220,225
70 READ X,Y
80 CIRCLE(X,Y),7,7
90 IF BV>-3 THEN BV=BV-1:GOTO 60
100 FOR Q=1 TO 3:FOR W=1 TO 3
110 P= (1000*RND) MOD 12:A(Q,W)=P:GOSUB 710
120 NEXT :NEXT
130 GOTO 230
140 Y$= INKEY$
150 IF Y$="" THEN GOTO 140
160 A= INSTR("+-1397qwas",Y$)
170 ON A GOTO 190,200,210,220,230,240,250,260,270,280
180 GOTO 140
190 K=1:GOTO 340
200 K=-1:GOTO 340
210 CIRCLE(I,J),43,0:CIRCLE(70 ,75 ),43,14:I= 70:J= 75:GOTO 140
220 CIRCLE(I,J),43,0:CIRCLE(270, 75),43,14:I=270:J= 75:GOTO 140
230 CIRCLE(I,J),43,0:CIRCLE(270,275),43,14:I=270:J=275:GOTO 140
240 CIRCLE(I,J),43,0:CIRCLE( 70,275),43,14:I= 70:J=275:GOTO 140
250 B(1,2)=B(1,2) XOR 1:PAINT(120,225),B(1,2),7:GOTO 290
260 B(2,2)=B(2,2) XOR 1:PAINT(220,225),B(2,2),7:GOTO 290
270 B(1,1)=B(1,1) XOR 1:PAINT(120,125),B(1,1),7:GOTO 290
280 B(2,1)=B(2,1) XOR 1:PAINT(220,125),B(2,1),7:GOTO 290
290 FOR X=1 TO 3:FOR Y=1 TO 3:G(X,Y)=0:NEXT :NEXT
300 FOR X=1 TO 2:FOR Y=1 TO 2
310 IF B(X,Y)=1 THEN G(X,Y)=1:G(X+1,Y)=1:G(X,Y+1)=1:G(X+1,Y+1)=1
320 NEXT :NEXT
330 GOTO 140
340 D=G((I+30)/100,(J+30)/100)
350 SCREEN 9,,NP XOR 1 ,NP:PCOPY NP,NP XOR 1
360 FOR X=1 TO 3 STEP 2-D:FOR Y=1 TO 3 STEP 2-D
370 IF G(X,Y)=D THEN P1=A(X,Y):A(X,Y)=(A(X,Y)+K+12) MOD 12:Q=X:W=Y ELSE GOTO 420
380  REM SCREEN 9,,NP XOR 1 ,NP:PCOPY NP,NP XOR 1
390 P=P1:C=0:GOSUB 710
400 P=A(X,Y):C=7:GOSUB 710
410 'SCREEN 9,,NPxor 1,NP XOR 1:NP=NP XOR 1
420 NEXT :NEXT
430 SCREEN 9,,NP XOR 1,NP XOR 1:NP=NP XOR 1
440 S=0
450 X=S MOD 3+1:Y=S\3+1
460 IF A(X,Y)>0 THEN GOTO 490
470 IF S<8 THEN S=S+1:GOTO 450 ELSE LOCATE 1,1:PRINT "nikises":END
480 END
490 GOTO 140
500  '****  ARXIKH SXEDIASH KYKLVN,YPOLOGISMOS fx(p),fy(p)
510 SCREEN 9
520 WINDOW (0,-75)-(639,425)
530 CLS
540 KEY OFF
550 FOR Y=75 TO 275 STEP 100
560 FOR X=70 TO 570 STEP 100
570 CIRCLE (X,Y),40
580 LINE (X+35,Y)-(X+40,Y)
590 LINE (X-35,Y)-(X-40,Y)
600 LINE (X,Y+35)-(X,Y+40)
610 LINE (X,Y-35)-(X,Y-40)
620 NEXT
630 NEXT
640 LINE (20,25)-(619,334),,B
650 LINE (319,25)-(319,334)
660 FX(0)=0: FY(0)=30:FX(3)=30:FY(3)=0  :FX(6)=0  :FY(6)=-30:FX(9 )=-30
670 FX(1)=15:FY(1)=26:FX(4)=26:FY(4)=-15:FX(7)=-15:FY(7)=-26:FX(10)=-26
680 FX(2)=26:FY(2)=15:FX(5)=15:FY(5)=-26:FX(8)=-26:FY(8)=-15:FX(11)=-15
690 FY(9)=0 :FY(10)=15: FY(11)=26
700 RETURN
710 '*** clock q,w; position p; color c
720 AX=-30+100*Q
730 AY=-25+100*W
740 LINE (AX,AY)-(AX+FX(P),AY+FY(P)),C
750 RETURN
