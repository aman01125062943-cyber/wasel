const PaymentService = require('../src/services/PaymentService');
const { db } = require('../src/database/db');
const NotificationService = require('../src/services/NotificationService');
const messageService = require('../src/services/baileys/MessageService');

// Mock dependencies
jest.mock('../src/database/db', () => ({
    db: {
        run: jest.fn(),
        get: jest.fn()
    }
}));
jest.mock('../src/services/NotificationService', () => ({
    getAdminSession: jest.fn()
}));
jest.mock('../src/services/baileys/MessageService', () => ({
    sendMessage: jest.fn()
}));

// Need to mock SessionManager if it's used directly, but checking the code it seems mostly used via NotificationService. 
// But PaymentService imports it. Just in case:
jest.mock('../src/services/baileys/SessionManager', () => ({}));

describe('PaymentService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('createPaymentRequest', () => {
        test('should create records and notify admin', async () => {
            const userId = 'u1';
            const planId = 'p1';
            const paymentData = {
                amount: 100,
                method: 'Vodafone',
                transactionRef: 'REF123',
                receiptPath: '/path.jpg'
            };

            // Spy on the notification method so we don't re-test its implementation here
            const notifySpy = jest.spyOn(PaymentService, 'notifyAdminWithReceipt')
                                 .mockResolvedValue(true);

            // Mock DB responses
            db.get.mockResolvedValueOnce(null); // No pending subscription
            db.run.mockResolvedValueOnce({ id: 'sub-new' }); // Insert subscription
            db.run.mockResolvedValueOnce({ id: 'pay-new' }); // Insert payment

            const result = await PaymentService.createPaymentRequest(
                userId, planId, paymentData.amount, paymentData.method, 
                paymentData.transactionRef, paymentData.receiptPath
            );

            // 1. Verify DB calls
            expect(result).toBe('pay-new');
            expect(db.run).toHaveBeenCalledTimes(2);
            expect(db.run).toHaveBeenCalledWith(
                expect.stringContaining('INSERT INTO payments'),
                expect.arrayContaining([userId, 'sub-new', paymentData.amount, paymentData.method])
            );

            // 2. Verify notification was called
            expect(notifySpy).toHaveBeenCalledTimes(1);
            expect(notifySpy).toHaveBeenCalledWith(
                'pay-new', userId, planId, paymentData.amount, 
                paymentData.method, paymentData.transactionRef, paymentData.receiptPath
            );

            // Clean up spy
            notifySpy.mockRestore();
        });
    });

    describe('notifyAdminWithReceipt', () => {
        test('should send message to admin', async () => {
            // Mock data
            NotificationService.getAdminSession.mockResolvedValue('sess-1');
            db.get.mockResolvedValueOnce({ name: 'User', phone: '123' }) // User
                .mockResolvedValueOnce({ name: 'Plan', duration_days: 30 }); // Plan

            await PaymentService.notifyAdminWithReceipt('pay-1', 'u1', 'p1', 100, 'Cash', 'Ref', '/img.jpg');

            expect(messageService.sendMessage).toHaveBeenCalledWith(
                'sess-1',
                '123',
                expect.stringContaining('طلب دفع جديد')
            );
        });
    });
});
