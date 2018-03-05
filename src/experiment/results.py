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


# next test
