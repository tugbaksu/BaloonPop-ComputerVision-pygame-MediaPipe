import pygame
import random
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector 
import time
import PIL

pygame.init()

# Ekran(window) oluşturma
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Blow Bubbles")


# FPS
fps = 60
clock = pygame.time.Clock()


# Webcam
cap = cv2.VideoCapture(0) #dahili kamerayı kullan
cap.set(3, 1280)  # width
cap.set(4, 720)  # height
#3 ve 4 genişlik ve yüksekliği ayarlar. 


# Ses dosyalarının yüklenmesi
pop_sound = pygame.mixer.Sound("2.Kaynaklar/pop_effect.mp3")  # Balon patlama efekti


# IMAGES
imgBalon = pygame.image.load("2.Kaynaklar/red_balloon.png").convert_alpha() #convert_alpha: PNG'nin saydamlığını korumak için kullanılır.
rectBalon = imgBalon.get_rect() #get rectangle dikdörtgen oluşturma
rectBalon.x, rectBalon.y = 500, 300 #rectangleın boyutları


# DEĞİŞKENLER-VARIABLES
speed = 5
score = 0  # Başlangıçta skorumuz ve her balon patlatıldığında aşağıdaki koda göre +10 olacak
startTime = time.time()
totalTime = 60


# DEDEKTÖR-DETECTOR
detector = HandDetector(detectionCon=0.8, maxHands=1) #dedection confidence


# ANA DONGU
start = True
game_started = False
while start:
    # Gerçekleşecek Olaylar
    for event in pygame.event.get():
        # Oyundan çıkma olayı
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()

        # Başlama düğmesine basılması
        if not game_started and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 560 <= mouse_pos[0] <= 860 and 350 <= mouse_pos[1] <= 500:
                game_started = True
                startTime = time.time()

    if game_started:
        # MANTIĞIN UYGULANMASI
        timeRemain = int(totalTime - (time.time() - startTime))  # Kalan zaman=şuanki zaman - başlangıç zamanı
        if timeRemain < 0:
            window.fill((255, 255, 255))  # Kalan zaman 0'dan küçük yani bitmişse ekranı beyaz göster
            font1 = pygame.font.Font("2.Kaynaklar/PressStart2P-Regular.ttf", 50)
            font2 = pygame.font.Font("2.Kaynaklar/PressStart2P-Regular.ttf", 80)
            text_score = font1.render(f'Skorun: {score}', True, (76, 205, 91))
            text_time = font2.render(f'Zaman Doldu!', True, (255, 13, 0))
            window.blit(text_score, (360, 220))
            window.blit(text_time, (210, 370))

        else:  # Zaman bitmemişse tüm oyun mantığı çalışsın ve oyun devam etsin sürekli
            # OpenCV ile kameranın ekrana yansıtılması
            success, img = cap.read()
            img = cv2.flip(img, 1)  # horizontal(1 bu anlamda 0=vertical) dikeyde görüntü dönücek ki sağ eli kaldırınca ekranda sol gibi gözükmemesini sağlar
            hands, img = detector.findHands(img, flipType=False)  # Elin algılanması

            rectBalon.y -= speed  # Balon nesnesinin speed değişkenini kadar piksel yukarı kaymasını sağlar.

            if rectBalon.y < 0:
                rectBalon.x = random.randint(100, img.shape[1] - 100)
                rectBalon.y = img.shape[0] + 50  # hight
                speed += 1  # Nesne hızını arttırma

            if hands:
                hand = hands[0]
                x, y = hand['lmList'][8]  # El algılanınca oluşan noktalardan 8 numaralı yani işaret parmağ ucunu seçtik
                if rectBalon.collidepoint(x, y):  # Eğer x,y noktası parmak ucundaki noktaya temas ederse
                    rectBalon.x = random.randint(100, img.shape[1] - 100)
                    rectBalon.y = img.shape[0] + 50
                    score += 10  # Her balon patlatıldığında score 10 artsın
                    speed += 0.5
                    pop_sound.play() 

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BU DÖNÜŞÜMÜ OpenCV BGR
            # Kullandığı ve pygame ise RGB kullandığı için yaptık
            imgRGB = np.rot90(imgRGB)  # Kamera ters şekilde açıldığı için 90 derece döndürüp düzeltildi
            frame = pygame.surfarray.make_surface(imgRGB)
            frame = pygame.transform.flip(frame, True, False)  # Kamera görüntüsünün yansıması alındı ve tam doğru görüntü oluşturuldu
            window.blit(frame, (0, 0))  # Frame değişkenini (0,0) pozisyonunda başlat
            window.blit(imgBalon, (rectBalon))

            font = pygame.font.Font("2.Kaynaklar/PressStart2P-Regular.ttf", 40)

            text_score = font.render(f'Skor: {score}', True, (76, 205, 91))
            text_time = font.render(f'Zaman: {timeRemain}', True, (76, 205, 91))

            window.blit(text_score, (35, 35))
            window.blit(text_time, (900, 35))

    else:
        # Başlangıç ekranı
        window.fill((209, 241, 255))
        font = pygame.font.Font("2.Kaynaklar/Workbench-Regular.ttf", 130)
        text = font.render("Blow Bubbles", True, (0, 96, 229))
        window.blit(text, (260, 300))

        # Başlatma düğmesinin özelliklerini belirleme
        start_button = pygame.Rect(500, 450, 280, 80)  # (x, y, width, height)
        pygame.draw.rect(window, (255,13,0), start_button,border_radius=20)  # Düğme rengi
        font = pygame.font.Font("2.Kaynaklar/PressStart2P-Regular.ttf", 40)  # Yazı tipi ve boyutu
        text = font.render("Başla", True, (255, 255, 255))  # Yazı rengi
        window.blit(text, (540, 475))  # Yazının konumu

    # Görüntüyü güncelleme
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
