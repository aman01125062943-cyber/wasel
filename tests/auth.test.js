// Mock dependencies BEFORE requiring the module under test
jest.mock('bcrypt');
jest.mock('../src/services/NotificationService', () => ({
    createAdminNotification: jest.fn().mockResolvedValue(true)
}));

const bcrypt = require('bcrypt');
const AuthService = require('../src/services/auth');
const { db } = require('../src/database/db');

// Mock the database dependency
jest.mock('../src/database/db', () => ({
    db: {
        get: jest.fn(),
        run: jest.fn(),
    },
}));

describe('AuthService', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('register', () => {
        const userData = {
            name: 'Test User',
            phone: '1234567890',
            email: 'test@example.com',
            password: 'password123',
            planId: 1
        };

        // We keep bcrypt for hashing in registration, but it's mocked.
        // Let's provide a mock implementation for hash.
        bcrypt.hash.mockResolvedValue('hashed-password');
        bcrypt.genSalt.mockResolvedValue('salt');


        test('should register new user successfully', async () => {
            // Mock 1: Check existing user (return null = not found)
            db.get.mockResolvedValueOnce(null);
            // Mock 2: Get plan (return plan object)
            db.get.mockResolvedValueOnce({
                id: 1,
                name: 'Basic Plan',
                duration_days: 30,
                is_trial: 0
            });
            // Mock 3 & 4: Insert User & Subscription
            db.run.mockResolvedValue({ id: 1 });

            const result = await AuthService.register(userData);

            expect(result).toHaveProperty('userId');
            expect(result).toHaveProperty('status', 'pending');
            expect(db.run).toHaveBeenCalledTimes(2);
            expect(db.run).toHaveBeenCalledWith(
                expect.stringContaining('INSERT INTO users'),
                expect.any(Array)
            );
            // Check if password was hashed
            expect(bcrypt.hash).toHaveBeenCalledWith('password123', 'salt');
        });

        test('should fail if phone/email already exists', async () => {
            // Mock 1: Check existing user (return found)
            db.get.mockResolvedValueOnce({ id: 'existing-id' });

            await expect(AuthService.register(userData))
                .rejects.toThrow('رقم الهاتف أو البريد الإلكتروني مسجل بالفعل');

            expect(db.run).not.toHaveBeenCalled();
        });

        test('should fail if plan does not exist', async () => {
            // Mock 1: Check existing user (null)
            db.get.mockResolvedValueOnce(null);
            // Mock 2: Get plan (null = not found)
            db.get.mockResolvedValueOnce(null);

            await expect(AuthService.register(userData))
                .rejects.toThrow('الباقة غير موجودة');
        });
    });

    describe('login', () => {
        test('should login with valid credentials', async () => {
            db.get.mockResolvedValueOnce({
                id: 'user-id',
                name: 'User',
                password_hash: 'hashed-password'
            });
            bcrypt.compare.mockResolvedValueOnce(true);

            const user = await AuthService.login('test@example.com', 'password123');
            expect(user).toHaveProperty('id', 'user-id');
            expect(bcrypt.compare).toHaveBeenCalledWith('password123', 'hashed-password');
        });

        test('should fail with invalid password', async () => {
            db.get.mockResolvedValueOnce({
                id: 'user-id',
                password_hash: 'hashed-password'
            });
            bcrypt.compare.mockResolvedValueOnce(false);

            await expect(AuthService.login('test@example.com', 'wrongpassword'))
                .rejects.toThrow('بيانات الدخول غير صحيحة');
            expect(bcrypt.compare).toHaveBeenCalledWith('wrongpassword', 'hashed-password');
        });

        test('should fail if user not found', async () => {
            db.get.mockResolvedValueOnce(null);

            await expect(AuthService.login('unknown@email.com', 'pass'))
                .rejects.toThrow('بيانات الدخول غير صحيحة');

            // bcrypt.compare should not be called if user is not found
            expect(bcrypt.compare).not.toHaveBeenCalled();
        });
    });
});
