# SmartRent360 Backend API

A comprehensive Django REST Framework backend for a property rental management platform connecting landlords, tenants, and administrators across East Africa.

## Features

### 1. User Management
- Role-based user system (Tenant, Landlord, Commissioner, Government, Admin)
- Token-based authentication
- User profiles with detailed information
- Account verification system
- Password management and security

### 2. Property Management
- Add, edit, and manage multiple properties
- Property types and amenities
- Multi-image upload support
- Property availability scheduling
- Location-based search with filters
- Property favorites/saved listings
- Advanced search by price, location, rooms, etc.

### 3. Booking & Lease Management
- Tenant applications for properties
- Landlord approval/rejection workflow
- Property visit scheduling
- Digital lease agreement system
- E-signature support

### 4. Payment & Finance
- Rent payment tracking
- Invoice generation
- Receipt management
- Payment schedules
- Platform commission tracking
- Multiple payment methods support

### 5. Messaging System
- Direct messaging between users
- Conversation threading
- File attachments
- Read status tracking
- System notifications
- Announcements

### 6. Reviews & Ratings
- Property and user reviews
- 5-star rating system
- Aspect-based ratings (cleanliness, location, value, safety)
- Review responses
- Helpful voting system
- Maintenance request tracking

## Technology Stack

- **Backend**: Django 4.2+
- **API**: Django REST Framework
- **Database**: MySQL
- **Authentication**: Token-based
- **Features**: Django Filters, CORS, Pagination

## Project Structure

```
smartrent360/
├── users_app/          # User management & authentication
├── properties_app/     # Property listings & management
├── bookings_app/       # Booking & lease agreements
├── payments_app/       # Payment tracking & invoices
├── messaging_app/      # Messaging & notifications
├── reviews_app/        # Reviews & ratings
└── smartrent360/       # Main project configuration
```

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip

### Setup Steps

1. **Clone the repository**
```bash
cd smartrent360
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
source venv/bin/activate      # On Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=smartrent360
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## API Endpoints

### Authentication
- `POST /api/v1/users/register/` - Register new user
- `POST /api/v1/users/login/` - Login user
- `POST /api/v1/users/logout/` - Logout user
- `GET /api/v1/users/me/` - Get current user profile
- `POST /api/v1/users/change_password/` - Change password

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}/` - Get user details
- `PATCH /api/v1/users/{id}/update_profile/` - Update profile
- `GET /api/v1/landlords/` - List landlord profiles
- `GET /api/v1/tenants/` - List tenant profiles

### Properties
- `GET /api/v1/properties/` - List properties
- `POST /api/v1/properties/` - Create property
- `GET /api/v1/properties/{id}/` - Get property details
- `PATCH /api/v1/properties/{id}/` - Update property
- `DELETE /api/v1/properties/{id}/` - Delete property
- `POST /api/v1/properties/{id}/upload_image/` - Upload property image
- `POST /api/v1/properties/{id}/toggle_favorite/` - Add/remove from favorites
- `GET /api/v1/properties/search/` - Advanced search

### Bookings
- `GET /api/v1/bookings/` - List bookings
- `POST /api/v1/bookings/apply_for_property/` - Apply for property
- `POST /api/v1/bookings/{id}/approve/` - Approve booking
- `POST /api/v1/bookings/{id}/reject/` - Reject booking
- `GET /api/v1/visits/` - List property visits
- `POST /api/v1/visits/schedule_visit/` - Schedule visit
- `GET /api/v1/leases/` - List leases
- `POST /api/v1/leases/create_lease/` - Create lease agreement

### Payments
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/record_payment/` - Record payment
- `GET /api/v1/payments/overdue_payments/` - Get overdue payments
- `GET /api/v1/invoices/` - List invoices
- `POST /api/v1/invoices/{id}/mark_paid/` - Mark invoice as paid
- `GET /api/v1/receipts/` - List receipts

### Messaging
- `GET /api/v1/messages/` - List messages
- `POST /api/v1/messages/send_message/` - Send message
- `GET /api/v1/conversations/` - List conversations
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/announcements/` - List announcements

### Reviews
- `GET /api/v1/reviews/` - List reviews
- `POST /api/v1/reviews/submit_review/` - Submit review
- `POST /api/v1/maintenance/` - Submit maintenance request
- `GET /api/v1/maintenance/open_requests/` - Get open requests

## Database Models

### Users
- User (Custom user model with roles)
- LandlordProfile (Extended landlord information)
- TenantProfile (Extended tenant information)

### Properties
- Property (Main property listing)
- PropertyType (Property categories)
- PropertyImage (Property photos)
- PropertyAmenity (Amenities list)
- PropertyAmenityLink (Property-Amenity relationship)
- SavedProperty (Favorites)

### Bookings
- Booking (Tenant applications)
- PropertyVisit (Property viewings)
- LeaseAgreement (Digital contracts)

### Payments
- Payment (Rent and other payments)
- Receipt (Payment receipts)
- Invoice (Monthly invoices)
- RentPaymentSchedule (Auto-payment setup)
- PlatformCommission (Commission tracking)

### Messaging
- Message (Direct messages)
- Conversation (Message threads)
- Notification (System notifications)
- Announcement (Platform announcements)

### Reviews
- Review (Property and user reviews)
- ReviewReply (Response to reviews)
- ReviewImage (Review images)
- ReviewHelpful (Helpful votes)
- MaintenanceRequest (Maintenance requests)

## Permissions

The system uses role-based permissions:

- **Tenant**: Can search properties, apply for bookings, make payments, leave reviews
- **Landlord**: Can manage properties, approve/reject applications, track payments
- **Commissioner**: Can verify users and landlords
- **Government**: Can access housing statistics and data
- **Admin**: Full system access

## Authentication

The API uses Token-based authentication. Include the token in headers:

```
Authorization: Token your-token-here
```

## Response Format

All API responses follow a standard format:

```json
{
    "data": { ... },
    "message": "Success message",
    "status": "success"
}
```

## Error Handling

Error responses include appropriate HTTP status codes and error messages:

```json
{
    "error": "Error message",
    "status": "error"
}
```

## CORS Configuration

The API is configured to accept requests from:
- http://localhost:3000 (Frontend development)
- http://localhost:8000 (Local development)

Update `CORS_ALLOWED_ORIGINS` in `settings.py` for production.

## Rate Limiting

API rate limits:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

## Contributing

1. Create a feature branch
2. Make your changes
3. Commit with clear messages
4. Push to the branch
5. Create a pull request

## Future Enhancements

- [ ] WhatsApp integration
- [ ] AI-powered property recommendations
- [ ] Offline mode support
- [ ] Multi-language support improvements
- [ ] IoT integration for smart homes
- [ ] Government system integration
- [ ] Mobile app (Flutter)
- [ ] Advanced analytics dashboard

## License

This project is proprietary software.

## Support

For issues and support, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: May 2026
