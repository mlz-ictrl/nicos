#
countfor = 1

# try at Bragg elastic signal with useful statistics


move(ss1, (-20, 20, -40, 40))
move(ss2, (-20, 20, -40, 40))
wait(ss1, ss2)


scan(ss1.left, -20, 2, 15, countfor)
maw(ss1.left, -20)

scan(ss1.right, 20, -2, 15, countfor)
maw(ss1.right, 20)


scan(ss1.bottom, -40, 2, 25, countfor)
maw(ss1.bottom, -40)

scan(ss1.top, 40, -2, 25, countfor)
maw(ss1.top, 40)



scan(ss2.left, -20, 2, 15, countfor)
maw(ss2.left, -20)

scan(ss2.right, 20, -2, 15, countfor)
maw(ss2.right, 20)

scan(ss2.bottom, -40, 2, 25, countfor)
maw(ss2.bottom, -40)

scan(ss1.top, 40, -2, 25, countfor)
maw(ss1.top, 40)
