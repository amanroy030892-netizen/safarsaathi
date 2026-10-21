# SafarSaathi Supercar Race (Car Racing Gaming Zone) 🎮🏎️

## 1. Overview & New Features
Is update mein purane top "Live Map" button ko replace karke ek exciting, real-time **Car Racing Gaming Zone** add kiya gaya hai jahan users coins ke sath 3-Car Supercar Race khel sakte hain.

### Key Rules & Mechanics:
1. **3 Supercars on Grid:**
   - Har race mein 3 sports cars participate karti hain (Lane 1, Lane 2, Lane 3).
2. **Dynamic Car Models & Designs Every Round:**
   - Har baar ek hi car nahi hoti. 18 alag-alag supercars (Ferrari F8, Lambo Huracán, Porsche 911, Mustang Shelby, Bugatti Chiron, McLaren 720S, Nissan GT-R, Toyota Supra, Corvette Z06, BMW M4, Aston Martin, Audi R8, Thar 4x4 Beast, etc.) ke pool se har round mein 3 bilkul nayi cars dynamically chuni jaati hain.
   - Har car ka unique SVG body, dynamic colors, custom racing stripes, aerofoil spoiler, headlights aur racing number visually generate hota hai.
3. **Winning Rule ("Sabse Kam Bet Wali Car Jeetegi"):**
   - Sabhi players aur simulated crowd ke bets milakar **jis gaadi par sabse kam total bet (Lowest Total Bet)** lagega, wahi car race jeetegi!
   - Agar aapne jeetne wali car (sabse kam bet wali car) par bet lagaya hai, to aapko **3x (300%) Winnings** milti hai!
4. **Coins Economy (1 Coin = ₹1):**
   - App ki currency **Coins (🪙)** hai, jahan **1 Coin ki value ₹1** hai.
   - Har naye user ko turant test karne ke liye **100 Coins (₹100 value) Free Welcome Bonus** milta hai.
   - Rozana **🎁 20 Free Coins Daily Bonus** claim karne ka feature bhi uplabdh hai.
5. **Instant QR Payment Coin Purchase:**
   - Jab bhi kisi user ke coins khatam honge ya wo naye coins khareedna chahega, to "➕ Buy Coins" par tap karke Jana Small Finance Bank UPI QR code (`mitali_qr_compact.svg` • `6901027507@nyes` • Mitali Kalita) par payment kar sakta hai.
   - PhonePe, Google Pay, Paytm, ya kisi bhi UPI app se 1-tap payment launcher uplabdh hai.
   - Payment ke baad 12-digit UTR enter karte hi coins turant bina kisi delay ke wallet mein credit ho jaate hain.

## 2. File Structure
* `index.html`: Main responsive web app jisme top navigation mein Gaming Zone button, 3-lane animated racetrack arena, betting cards, aur Buy Coins modal integrated hai.
* `game-racing.js`: Standalone modular game engine script jisme 18 supercars pool, SVG generator, audio synthesizer aur betting logic shamil hai.
* `style.css`: Clean responsive CSS styling.
* `sw.js`: Updated service worker (`v53-car-racing-gaming-zone`) jo stale cache ko purge karke naye changes turant browser mein deliver karta hai.
