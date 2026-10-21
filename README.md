# SafarSaathi Supercar Race (Car Racing Gaming Zone) 🎮🏎️

## 1. Overview & New Updates (Version 54)
User ke nirdesh anusaar Game Zone mein naye updates implement kiye gaye hain:

### Key Rules & Mechanics:
1. **3 Supercars on Grid:**
   - Har race mein 3 sports cars participate karti hain (Lane 1, Lane 2, Lane 3).
2. **Dynamic Car Models & Designs Every Round:**
   - Har baar ek hi car nahi hoti. 18 alag-alag supercars (Ferrari F8, Lambo Huracán, Porsche 911, Mustang Shelby, Bugatti Chiron, McLaren 720S, Nissan GT-R, Toyota Supra, Corvette Z06, BMW M4, Aston Martin, Audi R8, Thar 4x4 Beast, etc.) ke pool se har round mein 3 bilkul nayi cars dynamically chuni jaati hain.
   - Har car ka unique SVG body, dynamic colors, custom racing stripes, aerofoil spoiler, headlights aur racing number visually generate hota hai.
3. **Winning Rule ("Sabse Kam Bet Wali Car Jeetegi"):**
   - Sabhi players aur simulated crowd ke bets milakar **jis gaadi par sabse kam total bet (Lowest Total Bet)** lagega, wahi car race jeetegi!
4. **2x Payout Multiplier (Double Return):**
   - Payout ko 3x se badalkar **2x (200%)** kar diya gaya hai (jaise user ne manga: 50 coins lagane par 100 coins milenge, 100 lagane par 200 milenge).
5. **No Daily Free Bonus:**
   - Free daily bonus button ko poori tarah hata diya gaya hai.
6. **Coins Economy (1 Coin = ₹1):**
   - App ki currency **Coins (🪙)** hai, jahan **1 Coin ki value ₹1** hai.
   - Testing ke liye shuru mein 100 welcome coins milte hain taaki game check kiya ja sake.
7. **Instant QR Payment Coin Purchase:**
   - Coins khatam hone par "➕ Buy Coins" par tap karke Jana Small Finance Bank UPI QR code (`mitali_qr_compact.svg` • `6901027507@nyes` • Mitali Kalita) par payment kar sakte hain.
   - PhonePe, Google Pay, Paytm, ya kisi bhi UPI app se 1-tap payment launcher uplabdh hai. 12-digit UTR enter karte hi coins wallet mein credit ho jaate hain.
8. **💸 Customer Coin Withdrawal (विड्रॉल / पैसे निकालें):**
   - **Customer Withdrawal Option:** Gaming Zone header mein "💸 Withdraw (पैसे निकालें)" button add kiya gaya hai.
   - Customer apna UPI ID (PhonePe/GPay/Paytm) aur amount (minimum 50 coins = ₹50) daalkar withdrawal request submit kar sakta hai.
   - Coins turant wallet se kat jaate hain aur 1-tap WhatsApp alert Admin (`+91 6901027507`) ko chala jaata hai jisme Request ID, Amount, aur Customer UPI ID hoti hai.
   - **Admin Approval Desk (`admin.html`):** Admin Dashboard mein "🪙 Gaming Zone Coin Withdrawals" desk diya gaya hai jahan Admin customer ka UPI ID dekhkar direct 1-tap UPI app se payout bhej sakta hai aur "✅ Mark Paid & Send WhatsApp" par tap karke customer ko confirmation receipt bhej sakta hai.

## 2. File Structure
* `index.html`: Main responsive web app jisme Gaming Zone, 2x payout, 3-lane animated racetrack arena, Buy Coins modal aur Withdraw Coins modal integrated hai.
* `admin.html`: Fleet management, ride approvals, sponsor video ad manager, aur Customer Coin Withdrawals approval desk.
* `game-racing.js`: Standalone modular game engine script jisme 18 supercars pool, SVG generator, audio synthesizer aur 2x betting logic shamil hai.
* `style.css`: Clean responsive CSS styling.
* `sw.js`: Updated service worker (`v54-gaming-2x-withdraw-cashout`) jo stale cache ko purge karke naye changes turant browser mein deliver karta hai.
