# E-Shop Product Specifications

**Version:** 2.1
**Last Updated:** November 2025
**Product:** E-Shop Checkout System

---

## Overview

This document outlines the specifications for the E-Shop checkout system, including product catalog, discount policies, shipping options, and payment methods.

---

## Product Catalog

### Available Products

#### 1. Laptop Pro 15
- **Product ID:** LPTP-001
- **Price:** $1,299.99
- **Description:** High-performance laptop for professionals with 16GB RAM and 512GB SSD
- **Category:** Electronics
- **Stock:** In Stock
- **Weight:** 4.5 lbs

#### 2. Wireless Mouse
- **Product ID:** MOUSE-WL-001
- **Price:** $29.99
- **Description:** Ergonomic wireless mouse with 2.4GHz connectivity
- **Category:** Accessories
- **Stock:** In Stock
- **Weight:** 0.3 lbs

#### 3. USB-C Hub
- **Product ID:** HUB-USBC-001
- **Price:** $49.99
- **Description:** 7-in-1 USB-C hub with HDMI, USB 3.0 ports, and SD card reader
- **Category:** Accessories
- **Stock:** In Stock
- **Weight:** 0.2 lbs

---

## Discount Codes

### Active Discount Codes

#### SAVE15
- **Discount:** 15% off total purchase
- **Applicable To:** All products
- **Minimum Purchase:** None
- **Expiration:** December 31, 2025
- **Max Uses:** Unlimited
- **Description:** General promotional code for all customers

#### FIRST10
- **Discount:** 10% off total purchase
- **Applicable To:** All products
- **Minimum Purchase:** None
- **Expiration:** December 31, 2025
- **Max Uses:** One per customer
- **Description:** First-time customer discount
- **Restrictions:** Only valid for customers with no previous orders

#### WELCOME5
- **Discount:** 5% off total purchase
- **Applicable To:** All products
- **Minimum Purchase:** None
- **Expiration:** Never expires
- **Max Uses:** Unlimited
- **Description:** Welcome discount always available

### Invalid Discount Codes

Any discount code not listed above should be rejected with an error message: "Invalid discount code"

---

## Shipping Options

### Standard Shipping
- **Cost:** FREE
- **Delivery Time:** 5-7 business days
- **Tracking:** Provided
- **Description:** Standard ground shipping available for all products

### Express Shipping
- **Cost:** $10.00
- **Delivery Time:** 1-2 business days
- **Tracking:** Provided with real-time updates
- **Description:** Expedited shipping for urgent deliveries

---

## Payment Methods

### Supported Payment Methods

1. **Credit Card**
   - Visa, Mastercard, American Express, Discover
   - Secure PCI-compliant processing

2. **PayPal**
   - Redirect to PayPal for authentication
   - Support for PayPal balance and linked cards

3. **Bank Transfer**
   - Manual verification required
   - Processing time: 2-3 business days

---

## Checkout Process

### Required Customer Information

1. **Full Name** (Required)
   - Validation: Must not be empty
   - Used for shipping label

2. **Email** (Required)
   - Validation: Must be valid email format with @ symbol
   - Used for order confirmation and tracking

3. **Phone Number** (Optional)
   - Used for delivery contact

4. **Shipping Address** (Required)
   - Validation: Must not be empty
   - Used for package delivery

### Validation Rules

- All required fields must be filled before checkout
- Email must contain @ symbol
- Cart must contain at least one item
- Invalid discount codes should display error message
- Form errors should be displayed in red (#FF0000)

### Order Calculation

```
Subtotal = Sum of all cart items
Discount Amount = Subtotal × Discount Percentage (if code applied)
Shipping Cost = $0 (Standard) or $10 (Express)
Total = Subtotal - Discount Amount + Shipping Cost
```

### Successful Order

On successful order submission:
- Display success message: "Order submitted successfully! Thank you for your purchase."
- Clear shopping cart
- Reset all form fields
- Remove applied discount code

---

## Error Handling

### Form Validation Errors

- **Missing Name:** Display "Name is required"
- **Invalid Email:** Display "Valid email is required"
- **Missing Address:** Display "Address is required"
- **Empty Cart:** Display "Your cart is empty!"
- **Invalid Discount:** Display "Invalid discount code"

### Error Display

- Error messages should be shown in red color (#F44336)
- Error messages should appear below the relevant form field
- Multiple errors can be displayed simultaneously

---

## Business Rules

1. Discount codes are case-insensitive (SAVE15 = save15)
2. Only one discount code can be applied per order
3. Discount applies to subtotal only (before shipping)
4. Shipping cost is added after discount calculation
5. Free standard shipping is always available
6. Express shipping adds $10 regardless of order size

---

## Success Criteria

A successful checkout requires:
1. At least one item in cart
2. Valid customer name provided
3. Valid email address provided
4. Shipping address provided
5. Shipping method selected
6. Payment method selected

---

## Test Scenarios

### Positive Test Cases

- Add products to cart successfully
- Apply valid discount codes (SAVE15, FIRST10, WELCOME5)
- Complete checkout with all required fields
- Select different shipping methods
- Select different payment methods
- Calculate correct totals with discounts and shipping

### Negative Test Cases

- Submit checkout with empty cart
- Submit checkout without customer name
- Submit checkout without email
- Submit checkout with invalid email (no @ symbol)
- Submit checkout without shipping address
- Apply invalid discount code

---

**Document Owner:** Product Team
**Approval:** QA Team Lead
**Distribution:** Development, QA, Support Teams
