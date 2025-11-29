# E-Commerce Checkout - User Requirements

## Overview
This document describes the requirements for the e-commerce checkout system.

## Functional Requirements

### FR-1: Shopping Cart Management
- Users can add products to cart
- Users can remove products from cart
- Cart displays product name, price, and quantity
- Cart shows subtotal, discount, and total

### FR-2: Discount Code System
The system supports three discount codes:
- **SAVE15**: 15% discount on total
- **FIRST10**: 10% discount on total
- **WELCOME5**: 5% discount on total

Rules:
- Only one discount code can be applied per order
- Discount codes are case-sensitive
- Invalid codes show error message: "Invalid discount code"
- Discount applies before shipping costs

### FR-3: Customer Information
Required fields:
- Full Name (2-100 characters)
- Email (valid email format)
- Phone (10-15 digits)
- Shipping Address (minimum 10 characters)

Validation:
- All fields are mandatory
- Email must contain @ symbol
- Phone must be numeric only
- Form cannot be submitted with empty fields

### FR-4: Shipping Options
Two shipping methods available:
1. **Standard Shipping**: Free (5-7 business days)
2. **Express Shipping**: $10.00 (2-3 business days)

Default: Standard Shipping selected

### FR-5: Payment Methods
Three payment options:
1. Credit Card
2. PayPal
3. Bank Transfer

Default: Credit Card selected

### FR-6: Order Calculation
Formula:
```
Subtotal = Sum of (Product Price × Quantity)
Discount Amount = Subtotal × Discount Percentage
Discounted Total = Subtotal - Discount Amount
Shipping Cost = $0 (Standard) or $10 (Express)
Final Total = Discounted Total + Shipping Cost
```

## Non-Functional Requirements

### NFR-1: Performance
- Page load time: < 2 seconds
- Form submission: < 1 second
- Real-time price updates

### NFR-2: Usability
- Mobile responsive design
- Clear error messages
- Accessible form labels
- Visual feedback on interactions

### NFR-3: Security
- Input sanitization
- XSS protection
- HTTPS required for payment
- Secure form handling

## Error Scenarios

### ES-1: Invalid Discount Code
- Input: "INVALID123"
- Expected: Error message displayed
- Cart total unchanged

### ES-2: Empty Required Fields
- Input: Submit with empty name
- Expected: "This field is required" message
- Form submission blocked

### ES-3: Invalid Email Format
- Input: "notanemail"
- Expected: "Please enter a valid email" message
- Form submission blocked

### ES-4: Cart Total Zero
- Scenario: All items removed from cart
- Expected: Checkout button disabled
- Message: "Cart is empty"

## Success Criteria
- All discount codes work correctly
- Form validation prevents invalid submissions
- Order total calculated accurately
- All payment methods selectable
- Shipping cost added correctly
