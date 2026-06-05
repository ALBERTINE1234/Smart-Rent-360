# SmartRent360 API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
All endpoints (except registration and login) require token authentication.
Include the token in the Authorization header:
```
Authorization: Token your-token-here
```

## Response Format
All endpoints return JSON responses with the following structure:
```json
{
    "data": { ... },
    "message": "Success message",
    "status": "success"
}
```

---

## USER MANAGEMENT ENDPOINTS

### 1. Register User
**POST** `/users/register/`

**Request Body**
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+250788123456",
    "role": "tenant",
    "country": "Rwanda",
    "district": "Kigali"
}
```

**Response** (201 Created)
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+250788123456",
        "role": "tenant",
        "is_verified": false
    },
    "token": "your-token-here"
}
```

### 2. Login User
**POST** `/users/login/`

**Request Body**
```json
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Response** (200 OK)
```json
{
    "message": "Login successful",
    "token": "your-token-here",
    "user": { ... }
}
```

### 3. Get Current User
**GET** `/users/me/` (Authenticated)

**Response**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+250788123456",
    "role": "tenant",
    "is_verified": true,
    "profile_photo": "url-to-photo",
    "country": "Rwanda",
    "district": "Kigali",
    "preferred_language": "en",
    "created_at": "2026-05-29T10:30:00Z"
}
```

### 4. Update User Profile
**PATCH** `/users/me/update_profile/` (Authenticated)

**Request Body** (All fields optional)
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+250788123456",
    "preferred_language": "rw",
    "receive_notifications": true
}
```

### 5. Change Password
**POST** `/users/change_password/` (Authenticated)

**Request Body**
```json
{
    "old_password": "currentpassword",
    "new_password": "newpassword123",
    "new_password2": "newpassword123"
}
```

### 6. Logout User
**POST** `/users/logout/` (Authenticated)

---

## LANDLORD PROFILE ENDPOINTS

### 1. Get My Landlord Profile
**GET** `/landlords/my_profile/` (Authenticated - Landlord only)

**Response**
```json
{
    "id": 1,
    "user": { ... },
    "business_name": "John's Properties",
    "business_registration": "REG123",
    "tax_id": "TAX456",
    "bank_name": "Bank of Rwanda",
    "account_number": "1234567890",
    "is_verified": true,
    "verification_status": "approved",
    "total_properties": 5,
    "total_tenants": 8,
    "monthly_income": "50000.00",
    "rating": "4.5",
    "created_at": "2026-05-01T10:30:00Z"
}
```

### 2. Update Landlord Profile
**PATCH** `/landlords/my_profile/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "business_name": "Updated Business Name",
    "bank_name": "Bank of Rwanda",
    "mobile_money_provider": "MTN MoMo",
    "mobile_money_number": "+250788123456"
}
```

---

## TENANT PROFILE ENDPOINTS

### 1. Get My Tenant Profile
**GET** `/tenants/my_profile/` (Authenticated - Tenant only)

**Response**
```json
{
    "id": 1,
    "user": { ... },
    "employment_status": "employed",
    "employer_name": "Tech Company Ltd",
    "occupation": "Software Engineer",
    "monthly_income": "100000.00",
    "budget_min": "20000.00",
    "budget_max": "150000.00",
    "reference_name": "Jane Doe",
    "reference_phone": "+250799999999",
    "is_verified": true,
    "verification_status": "approved",
    "preferred_property_type": "apartment",
    "move_in_date": "2026-06-15",
    "rating": "5.0",
    "total_rentals": 3,
    "created_at": "2026-03-01T10:30:00Z"
}
```

### 2. Update Tenant Profile
**PATCH** `/tenants/my_profile/` (Authenticated - Tenant only)

**Request Body**
```json
{
    "employment_status": "self_employed",
    "monthly_income": "120000.00",
    "budget_min": "25000.00",
    "budget_max": "200000.00",
    "preferred_property_type": "house"
}
```

---

## PROPERTY ENDPOINTS

### 1. List Properties
**GET** `/properties/`

**Query Parameters**
```
?listing_type=rent&district=Kigali&min_price=20000&max_price=150000&min_rooms=2
?search=apartment&ordering=-created_at&page=1
```

**Response**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/v1/properties/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Modern Apartment in Kigali",
            "description": "Beautiful modern apartment...",
            "property_type": { "id": 1, "name": "Apartment" },
            "listing_type": "rent",
            "number_of_rooms": 2,
            "number_of_bathrooms": 1,
            "rent_price": "150000.00",
            "sale_price": null,
            "country": "Rwanda",
            "province": "Kigali City",
            "district": "Kigali",
            "village": "Kigali Central",
            "status": "available",
            "available_from": "2026-06-01",
            "rating": "4.5",
            "total_views": 250,
            "images": [ ... ],
            "amenities": [ ... ],
            "landlord": { ... },
            "created_at": "2026-05-15T10:30:00Z"
        }
    ]
}
```

### 2. Create Property (Landlord)
**POST** `/properties/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "title": "Modern Apartment in Kigali",
    "description": "Beautiful modern apartment with modern amenities",
    "property_type": 1,
    "listing_type": "rent",
    "number_of_rooms": 2,
    "number_of_bathrooms": 1,
    "rent_price": "150000.00",
    "deposit_required": "50000.00",
    "service_charges": "5000.00",
    "country": "Rwanda",
    "province": "Kigali City",
    "district": "Kigali",
    "sector": "Gasabo",
    "cell": "Umuja",
    "village": "Kigali Central",
    "street_address": "KG 123 Street",
    "available_from": "2026-06-01",
    "lease_term_months": 12,
    "has_kitchen": true,
    "has_water": true,
    "has_electricity": true,
    "furnished": false,
    "has_parking": true,
    "boundary_wall": true,
    "contact_method": "both"
}
```

**Response** (201 Created)
```json
{
    "id": 1,
    "title": "Modern Apartment in Kigali",
    ... (all property fields)
}
```

### 3. Get Property Details
**GET** `/properties/{id}/`

### 4. Update Property (Landlord only)
**PATCH** `/properties/{id}/`

### 5. Delete Property (Landlord only)
**DELETE** `/properties/{id}/`

### 6. Upload Property Image
**POST** `/properties/{id}/upload_image/` (Landlord only)

**Request** (multipart/form-data)
```
image: <file>
caption: "Living room view"
is_main_image: true
```

### 7. Add Property to Favorites
**POST** `/properties/{id}/toggle_favorite/` (Tenant only)

**Response**
```json
{
    "message": "Added to favorites"
}
```

### 8. Get My Properties
**GET** `/properties/my_properties/` (Landlord only)

### 9. Get My Favorite Properties
**GET** `/properties/my_favorites/` (Tenant only)

### 10. Advanced Search
**GET** `/properties/search/?min_price=20000&max_price=150000&country=Rwanda&district=Kigali&min_rooms=2`

---

## BOOKING ENDPOINTS

### 1. Apply for Property (Tenant)
**POST** `/bookings/apply_for_property/` (Authenticated - Tenant only)

**Request Body**
```json
{
    "property": 1,
    "move_in_date": "2026-06-15",
    "lease_term_months": 12,
    "number_of_occupants": 2,
    "message": "I am interested in this property..."
}
```

**Response** (201 Created)
```json
{
    "id": 1,
    "tenant": { ... },
    "property": { ... },
    "status": "pending",
    "move_in_date": "2026-06-15",
    "lease_term_months": 12,
    "number_of_occupants": 2,
    "message": "I am interested in this property...",
    "applied_at": "2026-05-29T10:30:00Z"
}
```

### 2. Get My Applications (Tenant)
**GET** `/bookings/my_applications/` (Authenticated - Tenant only)

### 3. Get Property Applications (Landlord)
**GET** `/bookings/property_applications/?property_id=1` (Authenticated - Landlord only)

### 4. Approve Booking (Landlord)
**POST** `/bookings/{id}/approve/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "message": "Application approved! Welcome!"
}
```

### 5. Reject Booking (Landlord)
**POST** `/bookings/{id}/reject/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "reason": "We selected another candidate"
}
```

---

## PROPERTY VISIT ENDPOINTS

### 1. Schedule Property Visit (Tenant)
**POST** `/visits/schedule_visit/` (Authenticated - Tenant only)

**Request Body**
```json
{
    "property": 1,
    "scheduled_date": "2026-06-01T14:30:00Z",
    "notes": "I would like to view the property"
}
```

### 2. Confirm Visit (Landlord)
**POST** `/visits/{id}/confirm/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "notes": "Confirmed for 2:30 PM"
}
```

### 3. Mark Visit as Completed
**POST** `/visits/{id}/complete/` (Authenticated)

---

## LEASE AGREEMENT ENDPOINTS

### 1. Create Lease Agreement (Landlord)
**POST** `/leases/create_lease/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "booking_id": 1,
    "terms": "Standard rental terms...",
    "special_conditions": "No pets allowed"
}
```

### 2. Tenant Signs Lease
**POST** `/leases/{id}/sign_tenant/` (Authenticated - Tenant only)

### 3. Landlord Signs Lease
**POST** `/leases/{id}/sign_landlord/` (Authenticated - Landlord only)

---

## PAYMENT ENDPOINTS

### 1. Record Payment (Landlord/Tenant)
**POST** `/payments/record_payment/`

**Request Body**
```json
{
    "payment_id": 1,
    "transaction_id": "MTN123456",
    "notes": "Payment received"
}
```

### 2. Get My Payments
**GET** `/payments/my_payments/` (Authenticated)

### 3. Get Overdue Payments
**GET** `/payments/overdue_payments/` (Authenticated)

### 4. Get Invoices
**GET** `/invoices/` (Authenticated)

### 5. Mark Invoice as Paid
**POST** `/invoices/{id}/mark_paid/` (Landlord only)

### 6. Get Pending Invoices
**GET** `/invoices/pending_invoices/` (Authenticated)

---

## MESSAGING ENDPOINTS

### 1. Send Message
**POST** `/messages/send_message/` (Authenticated)

**Request Body**
```json
{
    "recipient_id": 2,
    "message": "Hello, I'm interested in your property",
    "property_id": 1
}
```

### 2. Get Conversation with User
**GET** `/messages/conversation_with/?user_id=2` (Authenticated)

### 3. Mark Message as Read
**POST** `/messages/{id}/mark_as_read/` (Authenticated)

### 4. Get Unread Count
**GET** `/messages/unread_count/` (Authenticated)

### 5. Get All Conversations
**GET** `/conversations/my_conversations/` (Authenticated)

---

## NOTIFICATION ENDPOINTS

### 1. Get My Notifications
**GET** `/notifications/` (Authenticated)

### 2. Get Unread Notifications
**GET** `/notifications/unread/` (Authenticated)

### 3. Mark as Read
**POST** `/notifications/{id}/mark_as_read/` (Authenticated)

### 4. Mark All as Read
**POST** `/notifications/mark_all_as_read/` (Authenticated)

### 5. Clear All
**POST** `/notifications/clear_all/` (Authenticated)

---

## REVIEW ENDPOINTS

### 1. Submit Review
**POST** `/reviews/submit_review/` (Authenticated - Tenant only)

**Request Body**
```json
{
    "subject": "property",
    "property": 1,
    "booking": 1,
    "rating": 5,
    "title": "Excellent Property",
    "comment": "Very clean and well-maintained...",
    "cleanliness_rating": 5,
    "location_rating": 4,
    "value_rating": 4,
    "safety_rating": 5
}
```

### 2. Get Property Reviews
**GET** `/reviews/property_reviews/?property_id=1`

### 3. Get Landlord Reviews
**GET** `/reviews/landlord_reviews/?landlord_id=1`

### 4. Reply to Review (Landlord)
**POST** `/reviews/{id}/reply_to_review/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "reply_text": "Thank you for your kind review!"
}
```

---

## MAINTENANCE REQUEST ENDPOINTS

### 1. Submit Maintenance Request (Tenant)
**POST** `/maintenance/` (Authenticated - Tenant only)

**Request Body**
```json
{
    "property": 1,
    "booking": 1,
    "title": "Broken Faucet",
    "description": "The kitchen faucet is leaking",
    "priority": "high"
}
```

### 2. Assign Maintenance Request (Landlord)
**POST** `/maintenance/{id}/assign/` (Authenticated - Landlord only)

**Request Body**
```json
{
    "assigned_to_id": 3
}
```

### 3. Mark as Completed
**POST** `/maintenance/{id}/mark_completed/` (Authenticated)

**Request Body**
```json
{
    "completion_notes": "Faucet replaced successfully"
}
```

### 4. Get Open Requests
**GET** `/maintenance/open_requests/` (Authenticated)

---

## ERROR RESPONSES

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "error": "Permission denied"
}
```

### 404 Not Found
```json
{
    "error": "Not found"
}
```

### 400 Bad Request
```json
{
    "error": "Invalid request"
}
```

---

## Rate Limits

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

---

## Best Practices

1. Always include the Authorization header for authenticated endpoints
2. Use pagination for list endpoints (default: 20 items per page)
3. Include appropriate filters in search queries
4. Handle errors gracefully in your frontend
5. Cache property listings when possible to reduce API calls

---

For more information, see the main README.md file.
