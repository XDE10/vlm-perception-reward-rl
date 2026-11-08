# 项目三规范序列化增量预览说明

[30 题双定位原图核查单](<manual_link_review_30.md>)。机器预览：`data/project3_perception_preview/canonical_perception_preview.jsonl`。

Angle → Length → Parallel → Perpendicular → Tangent；每类按规范实体字典序及规范有理数值排序、去重，保留角顶点与相切角色。冲突隔离；原事实、原顺序和旧封存产物均未改变。

所有预览均 review_only=true、human_review=pending、training_approved=false；它们不能直接作为感知奖励金标。

- `cases`: 200
- `split_counts`: {'train': 200}
- `manual_links`: 30
- `input_visual_candidates`: 450
- `canonical_after_dedup`: 450
- `cases_with_nonempty_preview`: 162
- `quarantined_count`: 0
- `human_reviewed_count`: 0
- `training_approved_count`: 0

## 200 题规范预览

### ID 1826 / train:380

```text
<perception>Length(A,D)=10; Length(C,D)=4; Length(D,E)=5; Perpendicular(BE,DE)</perception>
```

### ID 1910 / train:679

```text
<perception></perception>
```

### ID 2013 / train:975

```text
<perception></perception>
```

### ID 498 / train:1388

```text
<perception>Angle(C,D,E)=57deg</perception>
```

### ID 1571 / train:301

```text
<perception>Length(A,D)=32/5; Length(B,C)=13; Perpendicular(CE,DE)</perception>
```

### ID 1975 / train:972

```text
<perception>Length(A,E)=10; Length(B,N)=7; Length(C,N)=61/5; Perpendicular(AE,EN)</perception>
```

### ID 351 / train:820

```text
<perception></perception>
```

### ID 1288 / train:1356

```text
<perception></perception>
```

### ID 540 / train:243

```text
<perception>Angle(K,L,S)=49/2deg; Angle(K,P,L)=28deg; Length(J,K)=8; Length(J,S)=10; Perpendicular(JK,KS); Perpendicular(MP,MS); Perpendicular(PQ,QS)</perception>
```

### ID 2044 / train:33

```text
<perception>Length(B,C)=12; Length(B,D)=4; Perpendicular(AC,BC); Perpendicular(BD,CD)</perception>
```

### ID 1603 / train:713

```text
<perception>Length(A,B)=7; Length(A,C)=3; Length(B,C)=6; Length(E,F)=9</perception>
```

### ID 304 / train:1795

```text
<perception>Length(L,M)=27/10</perception>
```

### ID 990 / train:338

```text
<perception>Length(B,D)=9; Length(C,D)=4; Perpendicular(AB,AC); Perpendicular(AD,BD)</perception>
```

### ID 734 / train:1758

```text
<perception></perception>
```

### ID 1361 / train:1059

```text
<perception>Angle(Q,P,T)=112deg; Angle(R,P,S)=130deg</perception>
```

### ID 1641 / train:792

```text
<perception>Length(B,D)=8; Length(C,D)=3; Perpendicular(AB,AC); Perpendicular(AD,BD)</perception>
```

### ID 556 / train:1313

```text
<perception></perception>
```

### ID 690 / train:1296

```text
<perception>Length(M,N)=9; Length(M,Q)=8; Length(N,P)=10; Length(P,Q)=7; Length(W,X)=4</perception>
```

### ID 924 / train:641

```text
<perception>Angle(A,C,B)=45deg; Length(A,B)=3; Perpendicular(AB,AC)</perception>
```

### ID 124 / train:1280

```text
<perception>Angle(S,R,U)=49deg; Length(C,D)=11; Length(R,U)=12</perception>
```

### ID 127 / train:1509

```text
<perception>Parallel(AJ,BH); Parallel(AL,CI)</perception>
```

### ID 1521 / train:2100

```text
<perception></perception>
```

### ID 1849 / train:1213

```text
<perception></perception>
```

### ID 857 / train:150

```text
<perception>Length(A,B)=15; Length(A,C)=5; Perpendicular(AC,BC); Perpendicular(BY,CY)</perception>
```

### ID 949 / train:2045

```text
<perception>Length(A,C)=4; Length(C,D)=3; Perpendicular(AC,CD)</perception>
```

### ID 1187 / train:1655

```text
<perception>Angle(A,B,C)=111deg; Angle(B,A,C)=19deg; Length(B,C)=41</perception>
```

### ID 1822 / train:809

```text
<perception>Perpendicular(AC,BC)</perception>
```

### ID 2057 / train:345

```text
<perception>Length(A,D)=10; Length(A,E)=17; Length(B,C)=22; Perpendicular(AE,BE)</perception>
```

### ID 1607 / train:132

```text
<perception>Length(J,M)=13; Length(M,X)=5; Perpendicular(MX,RX)</perception>
```

### ID 1656 / train:335

```text
<perception>Length(T,V)=13; Length(V,W)=2; Perpendicular(TU,UW); Perpendicular(TW,UW)</perception>
```

### ID 2014 / train:1768

```text
<perception>Angle(A,B,C)=17deg; Length(A,C)=33/5; Perpendicular(AB,AC)</perception>
```

### ID 1987 / train:489

```text
<perception>Angle(G,A,H)=28deg</perception>
```

### ID 1964 / train:1682

```text
<perception>Length(A,C)=19; Length(B,N)=10; Length(C,N)=20; Length(E,F)=2; Perpendicular(AF,BF); Perpendicular(CN,EN)</perception>
```

### ID 1943 / train:425

```text
<perception>Angle(B,A,C)=30deg; Angle(C,B,E)=60deg; Perpendicular(AC,CE); Perpendicular(AE,CE)</perception>
```

### ID 636 / train:1778

```text
<perception>Perpendicular(WX,WZ)</perception>
```

### ID 867 / train:1820

```text
<perception></perception>
```

### ID 805 / train:534

```text
<perception>Length(B,R)=4; Length(H,M)=5; Length(K,P)=3</perception>
```

### ID 1852 / train:681

```text
<perception></perception>
```

### ID 933 / train:963

```text
<perception>Length(J,M)=6; Perpendicular(KM,LM)</perception>
```

### ID 721 / train:1472

```text
<perception>Parallel(HS,JR); Parallel(HS,KQ); Parallel(KQ,LP)</perception>
```

### ID 1937 / train:1476

```text
<perception>Length(D,G)=10; Perpendicular(DF,FH)</perception>
```

### ID 855 / train:1706

```text
<perception>Angle(A,C,J)=96deg; Angle(C,A,E)=94deg; Parallel(AC,EJ)</perception>
```

### ID 718 / train:1748

```text
<perception>Length(A,B)=20; Length(A,D)=10; Perpendicular(AB,AC); Perpendicular(BC,BD)</perception>
```

### ID 1704 / train:2038

```text
<perception>Length(R,S)=4; Length(R,V)=5; Length(S,V)=5; Length(T,U)=9</perception>
```

### ID 1892 / train:1285

```text
<perception>Length(H,J)=5</perception>
```

### ID 321 / train:958

```text
<perception>Length(B,G)=10; Length(E,G)=10</perception>
```

### ID 1109 / train:1747

```text
<perception>Angle(A,B,D)=125deg; Angle(C,B,D)=155deg</perception>
```

### ID 476 / train:1052

```text
<perception>Angle(B,M,H)=12deg; Angle(E,B,F)=28deg; Length(A,E)=3</perception>
```

### ID 1567 / train:1769

```text
<perception>Angle(G,H,K)=65deg; Parallel(BL,EK)</perception>
```

### ID 1606 / train:64

```text
<perception>Length(L,M)=10; Length(M,N)=10; Perpendicular(MN,MP)</perception>
```

### ID 809 / train:488

```text
<perception>Length(J,K)=25; Length(N,P)=8; Length(N,Q)=12; Length(P,Q)=20</perception>
```

### ID 1820 / train:894

```text
<perception>Length(P,Q)=25; Length(Q,S)=5; Length(R,S)=10; Parallel(PQ,ST); Perpendicular(RS,RT)</perception>
```

### ID 1584 / train:1787

```text
<perception>Angle(N,M,O)=56deg; Parallel(FK,OP); Parallel(FK,QT)</perception>
```

### ID 754 / train:2009

```text
<perception>Length(F,H)=12; Length(G,H)=12; Perpendicular(EF,EG); Perpendicular(EH,GH)</perception>
```

### ID 1725 / train:1677

```text
<perception>Length(K,M)=22</perception>
```

### ID 93 / train:2029

```text
<perception>Length(B,D)=12; Length(C,D)=12; Perpendicular(BD,CD)</perception>
```

### ID 1509 / train:1076

```text
<perception></perception>
```

### ID 1916 / train:396

```text
<perception>Length(C,D)=10</perception>
```

### ID 943 / train:1872

```text
<perception>Length(A,Z)=4; Perpendicular(AX,XY); Perpendicular(AZ,YZ)</perception>
```

### ID 341 / train:1751

```text
<perception>Length(S,T)=49; Length(U,V)=21; Length(U,W)=29; Length(V,W)=20</perception>
```

### ID 1960 / train:1845

```text
<perception>Angle(P,M,Q)=72deg</perception>
```

### ID 902 / train:1437

```text
<perception>Angle(A,E,C)=63deg; Angle(B,A,D)=47deg; Angle(B,F,D)=136deg; Angle(D,A,E)=69deg</perception>
```

### ID 1576 / train:850

```text
<perception></perception>
```

### ID 1493 / train:684

```text
<perception>Length(A,E)=3; Length(B,C)=12; Length(C,F)=6; Length(E,H)=2</perception>
```

### ID 1263 / train:1068

```text
<perception>Parallel(BE,CD)</perception>
```

### ID 1838 / train:741

```text
<perception>Length(A,D)=8; Length(B,C)=6; Length(D,E)=5; Parallel(BE,CD)</perception>
```

### ID 1136 / train:1942

```text
<perception>Angle(R,Q,S)=43deg; Length(Q,S)=8; Length(Q,T)=8; Perpendicular(QS,RS); Perpendicular(QT,RT)</perception>
```

### ID 680 / train:1310

```text
<perception>Length(A,X)=5; Length(A,Y)=9; Perpendicular(AX,AZ); Perpendicular(AZ,YZ)</perception>
```

### ID 1331 / train:1130

```text
<perception></perception>
```

### ID 1163 / train:1223

```text
<perception>Length(B,D)=5</perception>
```

### ID 331 / train:1759

```text
<perception>Length(M,N)=39; Length(M,P)=36; Length(N,P)=15; Perpendicular(MP,NP)</perception>
```

### ID 1428 / train:63

```text
<perception></perception>
```

### ID 1366 / train:357

```text
<perception>Angle(K,J,M)=59deg; Angle(K,L,M)=67deg</perception>
```

### ID 568 / train:945

```text
<perception>Angle(J,H,L)=76deg; Angle(M,H,P)=44deg</perception>
```

### ID 761 / train:2076

```text
<perception>Length(A,B)=5; Length(B,C)=5; Perpendicular(AB,BC)</perception>
```

### ID 836 / train:2030

```text
<perception>Length(B,X)=12; Length(C,X)=13; Length(F,Y)=13/2; Perpendicular(BC,BX); Perpendicular(EF,EY)</perception>
```

### ID 1053 / train:256

```text
<perception></perception>
```

### ID 888 / train:2034

```text
<perception>Length(R,T)=6; Perpendicular(PT,QT)</perception>
```

### ID 2009 / train:1834

```text
<perception>Angle(X,Y,Z)=60deg; Angle(X,Z,Y)=60deg; Length(X,Y)=4; Length(X,Z)=4</perception>
```

### ID 884 / train:601

```text
<perception>Angle(E,B,N)=45deg; Length(A,N)=64/5; Length(B,N)=32/5; Perpendicular(AE,BE)</perception>
```

### ID 459 / train:370

```text
<perception>Length(A,B)=6; Length(A,C)=18/5; Length(C,D)=2; Perpendicular(BD,CD)</perception>
```

### ID 1007 / train:326

```text
<perception>Parallel(AK,JW); Parallel(BN,IL)</perception>
```

### ID 1904 / train:1793

```text
<perception>Angle(A,B,H)=30deg; Angle(G,C,H)=28deg; Length(A,F)=24; Length(A,H)=25; Length(B,H)=11; Perpendicular(AF,FH); Perpendicular(BD,DH); Perpendicular(BG,GH)</perception>
```

### ID 1289 / train:1948

```text
<perception>Length(A,D)=9; Length(C,D)=4; Perpendicular(AB,BC); Perpendicular(BD,CD)</perception>
```

### ID 853 / train:2057

```text
<perception>Perpendicular(GJ,KL)</perception>
```

### ID 1938 / train:493

```text
<perception>Angle(A,C,D)=54deg; Angle(A,D,B)=34deg; Angle(C,A,D)=49deg; Length(A,D)=29; Length(C,D)=25</perception>
```

### ID 1926 / train:1359

```text
<perception>Length(B,D)=3; Length(B,E)=5; Parallel(AE,CD)</perception>
```

### ID 742 / train:1645

```text
<perception>Length(F,K)=15</perception>
```

### ID 863 / train:815

```text
<perception>Angle(A,T,B)=135deg; Length(B,T)=5</perception>
```

### ID 538 / train:929

```text
<perception>Angle(E,C,O)=60deg; Length(B,O)=15; Length(C,O)=20; Perpendicular(AE,EO)</perception>
```

### ID 711 / train:866

```text
<perception>Angle(B,D,E)=82deg; Length(A,C)=15; Length(E,F)=46/5</perception>
```

### ID 14 / train:400

```text
<perception>Perpendicular(BD,BI); Perpendicular(IJ,IL); Perpendicular(JN,JP)</perception>
```

### ID 1495 / train:264

```text
<perception>Perpendicular(AD,AH)</perception>
```

### ID 209 / train:2061

```text
<perception>Angle(B,D,E)=60deg; Length(A,C)=16; Length(C,D)=23; Perpendicular(BE,DE)</perception>
```

### ID 955 / train:2005

```text
<perception></perception>
```

### ID 1781 / train:1238

```text
<perception>Perpendicular(AB,BC)</perception>
```

### ID 144 / train:1583

```text
<perception>Length(S,T)=22</perception>
```

### ID 985 / train:1592

```text
<perception>Angle(A,C,D)=54deg; Angle(A,D,B)=34deg; Angle(C,A,D)=49deg; Length(A,D)=29; Length(C,D)=25</perception>
```

### ID 1596 / train:186

```text
<perception>Angle(A,G,C)=60deg; Perpendicular(AG,DG)</perception>
```

### ID 1244 / train:664

```text
<perception>Perpendicular(QS,RS)</perception>
```

### ID 2099 / train:768

```text
<perception>Length(A,B)=17; Length(A,C)=7; Perpendicular(AB,AC)</perception>
```

### ID 36 / train:67

```text
<perception>Angle(A,B,D)=130deg; Angle(C,B,D)=95deg</perception>
```

### ID 1944 / train:375

```text
<perception>Angle(B,A,E)=23deg; Angle(C,A,E)=42deg; Angle(D,B,E)=83deg</perception>
```

### ID 1076 / train:837

```text
<perception>Length(A,B)=75; Length(B,C)=40; Perpendicular(AB,BC)</perception>
```

### ID 1022 / train:299

```text
<perception>Angle(P,V,T)=72deg; Angle(S,V,T)=75deg; Perpendicular(RV,SV)</perception>
```

### ID 965 / train:1760

```text
<perception>Length(A,B)=16; Length(A,C)=12</perception>
```

### ID 609 / train:1262

```text
<perception>Perpendicular(AO,CO)</perception>
```

### ID 1921 / train:1646

```text
<perception>Perpendicular(BG,DG)</perception>
```

### ID 1989 / train:1691

```text
<perception></perception>
```

### ID 1245 / train:1654

```text
<perception>Length(A,B)=5; Length(B,C)=6; Perpendicular(AB,AC)</perception>
```

### ID 1643 / train:1720

```text
<perception></perception>
```

### ID 681 / train:297

```text
<perception>Angle(J,K,L)=109deg; Length(L,M)=6</perception>
```

### ID 1647 / train:1515

```text
<perception>Length(A,B)=7; Length(A,I)=7; Perpendicular(AB,AI)</perception>
```

### ID 285 / train:1470

```text
<perception>Length(S,W)=8; Length(T,V)=10</perception>
```

### ID 967 / train:1631

```text
<perception>Parallel(WZ,XY)</perception>
```

### ID 452 / train:1802

```text
<perception>Angle(H,O,J)=79deg; Angle(K,O,L)=77deg</perception>
```

### ID 433 / train:2086

```text
<perception>Parallel(PT,QR)</perception>
```

### ID 1604 / train:1817

```text
<perception></perception>
```

### ID 1404 / train:1573

```text
<perception></perception>
```

### ID 17 / train:913

```text
<perception></perception>
```

### ID 268 / train:1629

```text
<perception></perception>
```

### ID 968 / train:12

```text
<perception>Angle(C,G,H)=42deg; Angle(G,C,H)=48deg; Parallel(CH,DG)</perception>
```

### ID 1274 / train:1803

```text
<perception>Angle(A,C,B)=45deg; Perpendicular(AB,AC)</perception>
```

### ID 545 / train:778

```text
<perception>Angle(B,D,G)=31deg</perception>
```

### ID 324 / train:1042

```text
<perception></perception>
```

### ID 638 / train:660

```text
<perception>Length(X,Y)=7; Length(X,Z)=14; Perpendicular(XY,YZ)</perception>
```

### ID 1206 / train:749

```text
<perception>Perpendicular(RV,SV); Perpendicular(RZ,YZ)</perception>
```

### ID 935 / train:1041

```text
<perception>Length(A,C)=19; Length(A,D)=15; Perpendicular(AB,AC); Perpendicular(BC,BD)</perception>
```

### ID 946 / train:1710

```text
<perception>Length(R,W)=14; Length(U,Z)=5</perception>
```

### ID 1021 / train:782

```text
<perception>Length(A,E)=3; Length(B,C)=4; Length(C,D)=5; Length(S,T)=18</perception>
```

### ID 1749 / train:949

```text
<perception>Angle(Y,X,Z)=124deg; Length(R,T)=13; Length(X,Y)=7</perception>
```

### ID 191 / train:619

```text
<perception>Angle(A,B,G)=34deg; Angle(B,C,G)=32deg; Length(A,E)=12; Length(A,G)=15; Perpendicular(AE,EG); Perpendicular(AF,FG); Perpendicular(CD,DG)</perception>
```

### ID 1195 / train:1431

```text
<perception></perception>
```

### ID 1547 / train:1764

```text
<perception></perception>
```

### ID 1089 / train:1972

```text
<perception>Length(C,M)=9/2; Length(D,M)=9/2</perception>
```

### ID 1683 / train:824

```text
<perception>Perpendicular(WX,WZ); Perpendicular(WX,XY); Perpendicular(WZ,YZ); Perpendicular(XY,YZ)</perception>
```

### ID 700 / train:1800

```text
<perception>Parallel(BE,CD)</perception>
```

### ID 1297 / train:83

```text
<perception>Length(A,C)=27</perception>
```

### ID 272 / train:1305

```text
<perception></perception>
```

### ID 424 / train:995

```text
<perception></perception>
```

### ID 704 / train:618

```text
<perception>Angle(K,J,M)=56deg</perception>
```

### ID 108 / train:455

```text
<perception>Length(F,G)=24</perception>
```

### ID 345 / train:769

```text
<perception>Angle(H,A,J)=47deg; Angle(K,A,L)=116deg</perception>
```

### ID 1923 / train:457

```text
<perception></perception>
```

### ID 1002 / train:1368

```text
<perception>Perpendicular(AM,MY); Perpendicular(DN,NZ)</perception>
```

### ID 1551 / train:836

```text
<perception>Angle(A,B,C)=73deg; Angle(A,C,B)=67deg; Length(A,C)=8</perception>
```

### ID 725 / train:281

```text
<perception>Length(A,P)=8; Perpendicular(AB,AP); Perpendicular(BC,CP)</perception>
```

### ID 1585 / train:387

```text
<perception>Length(B,D)=8</perception>
```

### ID 2031 / train:1794

```text
<perception>Length(B,D)=3; Length(C,D)=6; Length(D,F)=2</perception>
```

### ID 1846 / train:1398

```text
<perception>Length(A,W)=10; Length(A,Y)=2</perception>
```

### ID 901 / train:1863

```text
<perception>Length(C,E)=27/5; Perpendicular(BC,BD)</perception>
```

### ID 1120 / train:1808

```text
<perception>Parallel(MN,YZ)</perception>
```

### ID 1974 / train:582

```text
<perception>Length(C,E)=11</perception>
```

### ID 938 / train:1009

```text
<perception>Angle(V,W,Y)=67deg; Angle(W,Y,Z)=58deg; Angle(X,Z,Y)=65deg</perception>
```

### ID 1644 / train:1006

```text
<perception>Angle(A,B,C)=45deg; Length(A,B)=19; Perpendicular(AC,BC)</perception>
```

### ID 1304 / train:1067

```text
<perception>Length(B,C)=12; Length(C,E)=6</perception>
```

### ID 1426 / train:1496

```text
<perception>Angle(A,F,D)=120deg</perception>
```

### ID 265 / train:18

```text
<perception></perception>
```

### ID 1025 / train:1216

```text
<perception></perception>
```

### ID 103 / train:1459

```text
<perception>Angle(A,L,K)=100deg</perception>
```

### ID 467 / train:2078

```text
<perception>Angle(B,A,C)=60deg; Length(A,C)=5; Perpendicular(AC,BC)</perception>
```

### ID 2043 / train:680

```text
<perception>Length(F,I)=16</perception>
```

### ID 1055 / train:943

```text
<perception></perception>
```

### ID 987 / train:1166

```text
<perception>Length(A,D)=32; Length(B,D)=40; Perpendicular(AC,BC); Perpendicular(AD,BD)</perception>
```

### ID 845 / train:739

```text
<perception>Angle(M,P,R)=68deg; Parallel(DL,IN); Parallel(ES,GH)</perception>
```

### ID 1510 / train:1325

```text
<perception>Angle(B,G,D)=154deg; Tangent(AB,G)</perception>
```

### ID 417 / train:795

```text
<perception>Angle(B,A,C)=64deg; Length(A,B)=120; Length(A,C)=54</perception>
```

### ID 621 / train:1871

```text
<perception>Parallel(AK,JW); Parallel(BN,IL)</perception>
```

### ID 969 / train:2041

```text
<perception></perception>
```

### ID 1174 / train:1092

```text
<perception>Angle(C,A,D)=52deg; Length(A,C)=18</perception>
```

### ID 1003 / train:1676

```text
<perception>Angle(A,X,W)=57deg</perception>
```

### ID 1423 / train:890

```text
<perception></perception>
```

### ID 1484 / train:9

```text
<perception>Perpendicular(AB,AC)</perception>
```

### ID 2056 / train:242

```text
<perception>Length(G,H)=32; Length(X,Y)=20</perception>
```

### ID 1112 / train:729

```text
<perception>Length(R,S)=8; Length(S,T)=12; Perpendicular(RS,ST)</perception>
```

### ID 1063 / train:1467

```text
<perception>Angle(B,F,C)=72deg</perception>
```

### ID 811 / train:125

```text
<perception>Length(P,W)=6; Length(P,X)=8; Length(P,Y)=24; Length(P,Z)=8</perception>
```

### ID 1498 / train:1644

```text
<perception>Angle(A,F,C)=38deg; Angle(C,E,G)=52deg; Perpendicular(DE,DF)</perception>
```

### ID 598 / train:853

```text
<perception>Angle(A,D,E)=30deg; Angle(A,E,D)=45deg; Length(A,E)=8; Perpendicular(AG,DG)</perception>
```

### ID 860 / train:51

```text
<perception>Perpendicular(BQ,CQ); Perpendicular(BY,SY); Perpendicular(CP,SY)</perception>
```

### ID 1497 / train:615

```text
<perception>Length(D,G)=9; Length(F,K)=12</perception>
```

### ID 562 / train:998

```text
<perception>Length(A,C)=8; Length(B,C)=6; Perpendicular(AB,AS); Perpendicular(AC,CS)</perception>
```

### ID 1480 / train:451

```text
<perception>Angle(M,N,Q)=33deg; Angle(M,R,Q)=38deg; Angle(N,Q,P)=83deg; Length(M,R)=179/10; Length(N,Q)=77/5; Length(P,Q)=111/10; Length(P,R)=20</perception>
```

### ID 481 / train:262

```text
<perception>Angle(S,Q,T)=32deg</perception>
```

### ID 1057 / train:341

```text
<perception>Angle(B,X,C)=90deg</perception>
```

### ID 1008 / train:1652

```text
<perception></perception>
```

### ID 841 / train:898

```text
<perception>Angle(A,L,C)=35deg; Angle(G,C,K)=28deg; Angle(G,D,L)=25deg; Angle(G,E,L)=51deg; Perpendicular(AH,AL); Perpendicular(BC,CF); Perpendicular(BG,CG)</perception>
```

### ID 2004 / train:1623

```text
<perception>Angle(B,A,D)=80deg; Angle(B,A,E)=64deg; Angle(C,A,D)=112deg; Angle(C,A,L)=64deg; Angle(E,A,L)=40deg</perception>
```

### ID 1243 / train:1708

```text
<perception></perception>
```

### ID 451 / train:828

```text
<perception>Angle(A,N,B)=62deg; Length(A,B)=3; Perpendicular(AB,BN); Perpendicular(AD,DN)</perception>
```

### ID 2010 / train:1272

```text
<perception></perception>
```

### ID 1285 / train:442

```text
<perception>Length(B,C)=28; Length(B,D)=15; Length(C,D)=27</perception>
```

### ID 1743 / train:1360

```text
<perception></perception>
```

### ID 187 / train:229

```text
<perception>Angle(D,A,E)=130deg; Length(C,F)=3</perception>
```

### ID 1090 / train:74

```text
<perception>Perpendicular(AC,BC)</perception>
```

### ID 2050 / train:772

```text
<perception>Length(A,C)=16; Length(A,F)=20; Length(B,F)=7; Length(C,D)=11</perception>
```

### ID 1041 / train:652

```text
<perception></perception>
```

### ID 771 / train:1672

```text
<perception>Length(A,B)=20; Length(A,D)=18; Length(C,E)=16; Perpendicular(CE,DE)</perception>
```

### ID 16 / train:462

```text
<perception>Parallel(BE,CD)</perception>
```

### ID 1860 / train:835

```text
<perception>Angle(C,F,E)=60deg; Length(A,D)=8; Length(A,E)=4; Length(C,F)=10</perception>
```

