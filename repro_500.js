const { db, init } = require('./src/database/db');
const IslamicRemindersService = require('./src/services/IslamicRemindersService');
const PrayerTimesService = require('./src/services/PrayerTimesService');

async function test() {
    try {
        await init();
        console.log('--- Testing Islamic Reminders Logic ---');

        // Use a known user ID (admin from server.js)
        const userId = '1994'; // Common ID or find it
        const adminEmail = 'aman01125062943@gmail.com';
        const user = await db.get("SELECT id FROM users WHERE email = ?", [adminEmail]);

        if (!user) {
            console.log('Admin user not found, using generic test');
            return;
        }

        console.log('Testing for User ID:', user.id);

        // 1. Get/Create Config
        const config = await IslamicRemindersService.getOrCreateConfig(user.id);
        console.log('Config loaded');

        // 2. Get Settings
        const prayerSettings = await IslamicRemindersService.getPrayerSettings(config.id);
        console.log('Prayer settings loaded:', prayerSettings.length);

        const fastingSettings = await IslamicRemindersService.getFastingSettings(config.id);
        console.log('Fasting settings loaded');

        const adhkarSettings = await IslamicRemindersService.getAdhkarSettings(config.id);
        console.log('Adhkar settings loaded');

        const recipients = await IslamicRemindersService.getRecipients(config.id);
        console.log('Recipients loaded:', recipients.length);

        // 3. Prayer Times
        console.log('Calculating prayer times...');
        const prayerTimes = await PrayerTimesService.getPrayerTimes(config);
        console.log('Prayer times:', prayerTimes);

        const nextPrayer = await PrayerTimesService.getNextPrayer(config);
        console.log('Next prayer:', nextPrayer);

        console.log('✅ All logic passed successfully');

    } catch (err) {
        console.error('❌ Test Failed:', err);
    } finally {
        process.exit(0);
    }
}

test();
