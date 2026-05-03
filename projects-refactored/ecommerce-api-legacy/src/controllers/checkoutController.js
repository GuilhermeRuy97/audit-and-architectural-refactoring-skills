const CourseModel = require('../models/courseModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const db = require('../models/db');

// Visa cards start with "4" (IIN prefix range 4xxxxx — used as payment simulation signal)
const VISA_IIN_PREFIX = '4';

class NotFoundError extends Error {
  constructor(message) { super(message); this.name = 'NotFoundError'; }
}

class PaymentError extends Error {
  constructor(message) { super(message); this.name = 'PaymentError'; }
}

async function processCheckout(userId, courseId, cardNumber) {
  const course = await CourseModel.findActiveById(courseId);
  if (!course) {
    throw new NotFoundError('Course not found or inactive');
  }

  const paymentStatus = cardNumber.startsWith(VISA_IIN_PREFIX) ? 'PAID' : 'DENIED';
  if (paymentStatus === 'DENIED') {
    throw new PaymentError('Payment denied — only Visa cards accepted in this simulation');
  }

  const enrollmentId = await EnrollmentModel.create(userId, courseId);
  await PaymentModel.create(enrollmentId, course.price, paymentStatus);
  await db.run(
    "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
    [`Checkout course ${courseId} by user ${userId}`]
  );

  return { enrollmentId, courseTitle: course.title, amount: course.price };
}

module.exports = { processCheckout, NotFoundError, PaymentError };
