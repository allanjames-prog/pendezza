def send_booking_confirmation_email(booking):
    # You can implement real email sending later using Django's send_mail
    print(f"Booking confirmation email sent to {booking.user.email} for booking #{booking.id}")

def send_payment_receipt_email(booking, payment):
    print(f"Payment receipt sent to {booking.user.email} for booking #{booking.id}, amount: {payment.amount}")
