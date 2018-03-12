'''
File for all sorts of nonsense related to running tests.
A dumping ground for test output
'''
import matplotlib.pyplot as plt

# test vFiber requests being processed over time.
# list of (x, y) where x it time, and y is number of active client threads

l = [(1.0078420639038086, 3), (2.0219831466674805, 7), (3.037006139755249, 9), (4.0563061237335205, 9), (5.071716070175171, 12), (6.0749571323394775, 8), (7.078989028930664, 9), (8.089706182479858, 11), (9.1009840965271, 7), (10.122044086456299, 12), (11.133639097213745, 9), (12.144590139389038, 11), (13.156282186508179, 14), (14.16378402709961, 6), (15.177877187728882, 9), (16.187206029891968, 7), (17.204777002334595, 8), (18.21603012084961, 11), (19.23619318008423, 9), (20.25285315513611, 9), (21.263444185256958, 6), (22.271785020828247, 5), (23.27740216255188, 4), (24.291540145874023, 7), (25.305297136306763, 7), (26.327755212783813, 8), (27.34372305870056, 8), (28.34688711166382, 5), (29.36423110961914, 6), (30.37767720222473, 9), (31.39230513572693, 8), (32.40535306930542, 7), (33.41378617286682, 9), (34.43828201293945, 8), (35.460944175720215, 11), (36.46136808395386, 7), (37.47183799743652, 3), (38.48419499397278, 5), (39.50022101402283, 6), (40.50537610054016, 5), (41.51426100730896, 4), (42.52749300003052, 6), (43.53059005737305, 5), (44.54038906097412, 4), (45.55304002761841, 5), (46.556549072265625, 4), (47.57186317443848, 8), (48.59409213066101, 11), (49.60539102554321, 9), (50.61331510543823, 5), (51.639440059661865, 10), (52.6611270904541, 14), (53.685707092285156, 20), (54.70539903640747, 11), (55.72675704956055, 16), (56.737303018569946, 11), (57.75540804862976, 6), (58.75554418563843, 3), (59.78654599189758, 8), (60.802895069122314, 11)]
plt.title('active client processes')
plt.xlabel('time (seconds)')
plt.ylabel('number of client threads')
plt.plot(*zip(*l))
plt.show()


# requests completed per second, in one minute
l = [(1.0193240642547607, 0.0), (2.042206048965454, 0.0), (3.0435149669647217, 1.3142698634366088), (4.052638053894043, 0.987011410050926), (5.060554027557373, 1.383247755459447), (6.07001805305481, 1.3179532466091932), (7.080107927322388, 1.4124078478252633), (8.098769903182983, 1.3582309574787121), (9.105813026428223, 1.4276594481206124), (10.124733924865723, 1.4815204143943896), (11.128814935684204, 1.3478524071689753), (12.142756938934326, 1.5647187945497556), (13.14891505241394, 1.444986139484709), (14.162780046463013, 1.977012981077304), (15.189724922180176, 2.040853284626209), (16.193015098571777, 1.9144056749958935), (17.24545693397522, 2.3774377308162844), (18.255640029907227, 2.2458812691766448), (19.27712392807007, 2.126873290485959), (20.294032096862793, 2.611605212164474), (21.30951189994812, 2.4871522280211886), (22.328948974609375, 2.776664502682202), (23.332151889801025, 2.6572774038515283), (24.338876962661743, 2.8349705742731213), (25.349111080169678, 2.761438055110351), (26.36546301841736, 2.7308452709404363), (27.378840923309326, 2.739341676664909), (28.39876389503479, 2.6409600177391144), (29.423870086669922, 2.7528669669016765), (30.434813022613525, 2.825711461940006), (31.45737600326538, 2.73385803034153), (32.468376874923706, 2.9259239033094793), (33.48015809059143, 2.98684372186707), (34.48945498466492, 2.9864200534858263), (35.507400035858154, 2.900803773184816), (36.52390003204346, 2.9569679006143517), (37.52397394180298, 2.8781599776052595), (38.53420901298523, 2.854606408631154), (39.55741500854492, 2.9324464193361086), (40.57460594177246, 2.9082229453895048), (41.57616591453552, 2.9584257541409738), (42.58947491645813, 2.9819574026004854), (43.60743594169617, 2.91234733841726), (44.61798596382141, 2.9136232214831654), (45.629539012908936, 2.936694143723223), (46.63682007789612, 2.873266225617092), (47.64948010444641, 2.917135710511755), (48.673989057540894, 2.8968244175202926), (49.68283200263977, 2.8983855025081686), (50.70533204078674, 2.8399380144906297), (51.72398591041565, 2.9773420839361306), (52.73223304748535, 2.9773061167089505), (53.74682307243347, 2.9955258896516295), (54.75753402709961, 2.976759324467223), (55.7752320766449, 2.9762314529124154), (56.797504901885986, 2.9754828190417264), (57.81091499328613, 2.9752167046651175), (58.820971965789795, 2.9921300875878316), (59.832244873046875, 2.991697877621095), (60.84576487541199, 2.958299568894707)]

plt.title('completed requests')
plt.xlabel('time (seconds)')
plt.ylabel('requests completed')
plt.plot(*zip(*l))
plt.show()
