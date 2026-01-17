const { db, init } = require('./src/database/db');

async function audit() {
    try {
        await init();
        console.log('--- Database Schema Audit ---');

        const tables = await db.all("SELECT name FROM sqlite_master WHERE type='table'");
        console.log('Tables:', tables.map(t => t.name).join(', '));

        const tablesToCheck = ['islamic_reminders_config', 'prayer_settings', 'adhkar_settings', 'fasting_settings'];

        for (const table of tablesToCheck) {
            const info = await db.all(`PRAGMA table_info(${table})`);
            console.log(`\nTable: ${table}`);
            if (info.length === 0) {
                console.log('❌ Table NOT FOUND');
            } else {
                info.forEach(col => console.log(` - ${col.name} (${col.type})`));
            }
        }

    } catch (err) {
        console.error('Audit Error:', err);
    }
}

audit();
