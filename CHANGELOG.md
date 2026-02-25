# CHANGELOG

## Drag-and-Drop Room Arrangement Page - February 25, 2026

### User Request
A page where players can be dragged and dropped between rooms. Each player should be a tile showing their name and their three chosen names. Room containers with 3 slots each. Number of rooms = ceil(selections / 3) + 1. Shows all players that have made a selection.

### What Was Created/Modified

- [core/views.py](core/views.py) — Added `RoomArrangeView` (GET, builds page context with serialised player/room JSON) and `SaveRoomArrangeView` (POST JSON, atomically rebuilds `RoomAssignment` rows; skips finalized rooms)
- [core/urls.py](core/urls.py) — Added `rooms/arrange/` → `core:room_arrange` and `rooms/arrange/save/` → `core:save_room_arrange`
- [core/templates/core/base.html](core/templates/core/base.html) — Added "Arrange Rooms" link in desktop and mobile nav; added `{% block extra_js %}` slot before `</body>`
- [core/templates/core/room_arrange.html](core/templates/core/room_arrange.html) — New template: unassigned player pool, responsive room grid, SortableJS drag-and-drop, Save button with AJAX + toast feedback

### How to Use
1. Log in as admin and click **Arrange Rooms** in the nav.
2. Drag player tiles from the unassigned pool (or other rooms) into any room container.
3. Tiles show the player's name and their three roommate choices.
4. A counter badge on each room turns green at exactly 3 players and red if over capacity.
5. Finalized rooms are locked (grey, not draggable).
6. Click **Save Layout** — the layout is POSTed as JSON and the page reloads with fresh DB state.

### Technical Details
- SortableJS 1.15.6 loaded from jsDelivr CDN — no new Python dependencies.
- Django context passes three JSON data islands (`players-data`, `rooms-data`, `unassigned-data`) as `<script type="application/json">` elements so the JS bootstraps without an extra API call.
- `SaveRoomArrangeView` uses a single `transaction.atomic()` block; new rooms (client-side `room_id: null`) are created on save and the page reload refreshes their UUIDs.
- `needed_rooms = ceil(n_players / 3) + 1` is computed in the view and passed to the template.



### User Request
favicon is missing, can you create one for this project? could you also create an svg icon to use instead of "Roommate Admin" in the navbar?

### What Was Created

#### New Static Assets
- **[core/static/core/img/favicon.svg](core/static/core/img/favicon.svg)**
  - Created SVG favicon with door/roommate theme
  - Blue circle background (#3B82F6)
  - Dark door with center split representing roommates
  - Gold door knobs
  - Number "3" at bottom representing 3 roommate selections
  
- **[core/static/core/img/logo.svg](core/static/core/img/logo.svg)**
  - Created SVG logo for navbar
  - 32x32 pixel optimized size
  - Blue circular badge design
  - Door icon with split in middle
  - Small bed icons in corners for hotel/room theme
  - Matches favicon design language

#### Template Changes
- **[core/templates/core/base.html](core/templates/core/base.html)**
  - Added `{% load static %}` tag in head section
  - Added favicon link: `<link rel="icon" type="image/svg+xml" href="{% static 'core/img/favicon.svg' %}">`
  - Replaced text "Roommate Admin" with logo image and text combo
  - Logo visible on all screen sizes (h-8 w-8)
  - Text "Roommate Admin" hidden on mobile (`hidden md:inline`) to save space
  - Made logo clickable, linking to dashboard
  - Added flex layout with spacing for logo + text

### Design Details

**Icon Theme:**
- Door with vertical split = roommates/shared space
- Blue color scheme matches Tailwind's primary blue
- Professional but friendly appearance
- SVG format = crisp at any resolution, small file size

**Responsive Behavior:**
- Desktop: Shows logo + "Roommate Admin" text
- Mobile/Tablet: Shows logo only (text hidden to save navbar space)
- Logo always clickable to return to dashboard

### Technical Details
- Using SVG format for both favicon and logo (modern, scalable)
- Favicon auto-detected by browsers via `<link rel="icon">`
- Static files served from `core/static/core/img/` directory
- Django's `{% static %}` template tag handles URL generation
- No additional static file configuration needed (already set in base.py)

## Sticky Navigation & Overlay Mobile Menu - February 21, 2026

### User Request
Can you make the title bar sticky so it's always visible, and on mobile open the hamburger menu over the content below instead of bumping it down?

### What Was Modified

#### Template Changes
- **[core/templates/core/base.html](core/templates/core/base.html)**
  - Added `sticky top-0 z-50` classes to nav element for sticky positioning
  - Added `relative` class to nav for positioning context
  - Changed mobile menu from block layout to `absolute` positioning
  - Mobile menu now uses `top-full left-0 right-0` to overlay content below the navbar
  - Added `bg-white shadow-lg` to mobile menu for proper overlay appearance

### How It Works

**Sticky Navigation:**
- Navigation bar stays fixed at the top of the viewport when scrolling
- Uses `z-50` to ensure it stays above page content
- Works on all screen sizes (mobile and desktop)

**Overlay Mobile Menu:**
- Mobile menu now appears as an overlay below the navigation bar
- Does not push page content down when opened
- Positioned absolutely relative to the nav container
- Full width (`left-0 right-0`) for proper mobile UX

### Technical Details

- `sticky top-0`: Makes nav stick to top of viewport while scrolling
- `z-50`: High z-index ensures navbar stays on top
- `relative`: Provides positioning context for absolute mobile menu
- `absolute top-full`: Positions mobile menu directly below navbar (100% from top)
- Mobile menu overlay preserves page layout without content reflow

---

## Mobile Hamburger Menu - February 21, 2026

### User Request
The menu for the page doesn't work on mobile. Can you add a hamburger menu that is used on small devices?

### What Was Modified

#### Template Changes
- **[core/templates/core/base.html](core/templates/core/base.html)**
  - Added hamburger menu button (visible only on mobile devices with `sm:hidden` class)
  - Added mobile menu panel with all navigation links (Dashboard, Players, Selections, Admin, Profile)
  - Added user info and logout button in mobile menu
  - Hid desktop username/logout on mobile with `hidden sm:inline` and `hidden sm:block` classes
  - Added JavaScript to toggle mobile menu visibility
  - Menu button shows hamburger icon (☰) when closed and X icon when open

### How to Use

On mobile devices (screen width < 640px):
1. Click the hamburger menu button (☰) in the top-right corner
2. The mobile menu slides down showing all navigation links
3. Click any link to navigate
4. Click the X icon to close the menu

On desktop (screen width ≥ 640px):
- The standard horizontal menu remains visible
- Hamburger menu button is hidden

### Technical Details

- Uses Tailwind CSS responsive breakpoints (`sm:` prefix for ≥640px)
- Vanilla JavaScript for menu toggle (no external dependencies)
- Icons are inline SVG for faster loading
- Mobile menu includes user authentication info and logout button
- Menu state managed via CSS class toggling (`hidden` class)

---

## Icelandic Alphabet Sorting Support - February 21, 2026

### User Request
The sorting of names on the player page uses the English alphabet. It should account for Icelandic sorting. Á should come after A and before B, for example.

### What Was Modified

#### Settings Changes
- **[roommate/settings/base.py](roommate/settings/base.py#L76-L78)**
  - Changed `LANGUAGE_CODE` from `"en-us"` to `"is-is"` (Icelandic)
  - Changed `TIME_ZONE` from `"UTC"` to `"Atlantic/Reykjavik"`

#### Model & Database Changes
- **[core/models.py](core/models.py#L19-L27)**: Added comment indicating Icelandic collation
- **Migration 0005_add_icelandic_collation_to_name.py**: Database-specific collation
  - For PostgreSQL (production): Applies `is_IS` collation to `name` field
  - For SQLite (development): Skips collation (not supported)
  - Uses `RunPython` migration to conditionally apply based on database vendor

### How It Works

**Icelandic Alphabet Order**: A, Á, B, D, Ð, E, É, F, G, H, I, Í, J, K, L, M, N, O, Ó, P, R, S, T, U, Ú, V, X, Y, Ý, Þ, Æ, Ö

- In **production (PostgreSQL)**: The `name` column uses native `is_IS` collation for proper Icelandic sorting
- In **development (SQLite)**: Basic alphabetical sorting (SQLite doesn't support Icelandic collation natively)
- Player names will be sorted correctly in the player list view according to Icelandic alphabet rules

### Technical Details
- PostgreSQL supports ICU collations including `is_IS` for Icelandic
- SQLite has limited collation support, so we use conditional migration
- The migration checks `connection.vendor` to apply collation only for PostgreSQL
- `ordering = ["name"]` in the Player model uses the database-level collation

---

## Formatter Configuration Added - February 21, 2026

### User Request
The code formatter was splitting Django template variables across multiple lines (e.g., `{{` on one line and `player.name }}` on the next), which causes rendering issues. Need to configure the formatter to prevent this.

### What Was Created
Created formatter configuration files to prevent template variable wrapping:

#### Configuration Files
- **[.prettierrc.json](.prettierrc.json)**: Prettier configuration
  - HTML files: `printWidth: 200` (prevents line wrapping)
  - HTML files: `htmlWhitespaceSensitivity: "ignore"` (better template handling)
  - HTML files: `bracketSameLine: true` (compact tag formatting)
  - Python files: `printWidth: 88` (Black standard)

- **[.vscode/settings.json](.vscode/settings.json)**: VS Code editor settings
  - Prettier as default formatter for HTML/Django templates
  - Black formatter for Python files
  - Line length: 200 for HTML, 88 for Python
  - Format on save enabled

- **[.prettierignore](.prettierignore)**: Exclude patterns
  - Build outputs, dependencies, generated files

- **[.editorconfig](.editorconfig)**: Editor-agnostic configuration
  - Max line length: 200 for HTML files
  - Consistent indentation rules across file types

### How It Works
The wide `printWidth` setting (200 characters) for HTML files ensures Django template variables like `{{ player.name }}` remain on single lines instead of being split during auto-formatting.

### Technical Details
- Prettier will now format HTML with 200-char width instead of default 80
- VS Code will apply these settings on save
- EditorConfig ensures consistency across different editors

---

## Bugfix: Player Import Template Variable Rendering - February 21, 2026

### Issue
When importing players, the import results table showed `{{ player.name }}` as literal text instead of rendering the actual player name. The error table similarly showed `{{ error.line }}` as literal text.

### Fix
Fixed Django template variable syntax in [core/templates/core/player_import.html](core/templates/core/player_import.html):
- Lines 93-94: Moved `{{ player.name }}` to a single line (was split across two lines)
- Lines 133-134: Moved `{{ error.line }}` to a single line (was split across two lines)

**Root Cause**: Template variables split across multiple lines can cause rendering issues where Django treats them as literal text rather than variables to interpolate.

**Testing**: Import players using the import feature and verify that the success/error tables display actual data instead of template variable syntax.

---

## Player Page Enhancements - February 21, 2026

### User Request
I need a few changes to the players page:
1. Make phone and email optional
2. Add a column to show if the selection link has been used
3. Pagination doesn't work - there is no way for the user to switch between pages
4. Add an import feature with comma-separated records validation

### What Was Created/Modified

#### Model Changes
- **Player Model** ([core/models.py](core/models.py#L19-L25))
  - Made `phone` field optional with `blank=True, null=True`
  - Made `email` field optional with `blank=True, null=True`
  - Generated migration `0004_make_phone_email_optional.py`

#### Player List View Enhancements
- **New Column**: Added "Link Used" column to player list table
  - Shows green "Yes" badge if selection link has been used
  - Shows gray "No" badge if link exists but not used
  - Shows "-" if no link has been generated
  - Reads from `SelectionLink.is_used` field

- **Fixed Pagination** ([core/templates/core/player_list.html](core/templates/core/player_list.html#L102-L152))
  - Added proper page number navigation controls
  - Shows current page highlighted in indigo
  - Displays page numbers with ellipsis for large page counts
  - Shows Previous/Next arrows
  - Mobile-responsive design with separate mobile pagination controls

- **Display Empty Values**: Phone and email now show "-" when not provided

#### Player Import Feature
- **Import View** ([core/views.py](core/views.py#L82-L181))
  - New `PlayerImportView` class-based view
  - Processes comma-separated text input (one player per line)
  - Validates each line with flexible format support:
    - Name only: `John Doe`
    - Name and phone: `John Doe, 555-1234`
    - Name and email: `John Doe, john@example.com`
    - Name, phone, and email: `John Doe, 555-1234, john@example.com`
  - Auto-detects email vs phone by checking for `@` and `.`
  - Uses atomic transactions for each player creation
  - Returns detailed summary with:
    - Count of successfully imported players
    - List of imported players with their data
    - List of failed rows with line numbers and error messages

- **Import Template** ([core/templates/core/player_import.html](core/templates/core/player_import.html))
  - Clean Tailwind UI with format instructions
  - Large textarea for bulk input
  - Results section showing:
    - Success table with green highlight
    - Error table with red highlight showing line number, data, and error
  - Back button to return to player list

- **Import Button**: Added "Import Players" button to player list page header

#### URL Configuration
- Added route: `players/import/` → `PlayerImportView`

### How to Use

**Import Players:**
1. Navigate to Players page
2. Click "Import Players" button
3. Enter comma-separated data (one player per line)
4. Click "Import Players" to process
5. Review success/error summary
6. Failed rows show specific error messages for correction

**View Link Status:**
- Player list now shows if selection links have been used in the "Link Used" column

**Navigate Pages:**
- Use pagination controls at bottom of player list to switch between pages
- Click page numbers directly or use Previous/Next arrows

### Technical Implementation
- Email validation uses basic `@` and `.` detection
- Phone and email fields handle NULL values in database
- Import view uses Django's transaction.atomic() for data integrity
- Pagination shows up to 5 page numbers around current page
- All changes follow project's Google docstring and type hint standards

## Production Deployment Setup - February 16, 2026

### User Request
Deploy the project to production using Docker Compose with Nginx as proxy and Certbot to handle certificates from Let's Encrypt. Use Cloudflare DNS authentication when generating certificates. All secrets and connection strings should be configured in environment variables.

### What Was Created

#### Docker Configuration
- **Dockerfile**: Multi-stage production-ready Django application container
  - Python 3.14 slim base image
  - Gunicorn WSGI server with 4 workers
  - Non-root user for security
  - Health checks configured
  - Automated static file collection

- **docker-compose.yml**: Complete orchestration with 7 services
  - `db`: PostgreSQL 16 with health checks
  - `redis`: Redis 7 for caching and Celery broker
  - `web`: Django application with Gunicorn
  - `celery`: Background task worker
  - `celery-beat`: Periodic task scheduler
  - `nginx`: Reverse proxy with SSL termination
  - `certbot`: Automated SSL certificate management

- **entrypoint.sh**: Container initialization script
  - Waits for database and Redis availability
  - Runs migrations automatically
  - Collects static files
  - Ensures proper startup order

#### Nginx Configuration
- **nginx/nginx.conf**: Main Nginx configuration
  - Optimized worker processes
  - Gzip compression enabled
  - 20MB client upload limit
  - Security headers

- **nginx/conf.d/default.conf**: Site-specific configuration
  - HTTP to HTTPS redirect
  - SSL/TLS 1.2 and 1.3 support
  - Modern cipher suites
  - Security headers (HSTS, XSS protection, etc.)
  - Static and media file serving with caching
  - Proxy configuration for Django application

#### Django Settings Restructure
- **roommate/settings/base.py**: Shared settings
- **roommate/settings/dev.py**: Development environment
- **roommate/settings/prod.py**: Production environment with:
  - PostgreSQL database configuration
  - Redis caching and sessions
  - Celery configuration
  - Security settings (SSL, HSTS, secure cookies)
  - Email configuration support
  - Comprehensive logging

#### Celery Setup
- **roommate/celery.py**: Celery application configuration
- **roommate/__init__.py**: Auto-import Celery app
- Configured for background tasks and scheduled jobs

#### Environment Configuration
- **.env.prod.example**: Template for production environment variables
  - Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
  - Database credentials
  - Redis password
  - Email configuration
  - Let's Encrypt settings
  - Cloudflare API token

- **certbot/cloudflare.ini.example**: Cloudflare DNS credentials template
  - API token configuration
  - Instructions for token creation

#### Deployment Scripts
- **init-letsencrypt.sh**: Initial SSL certificate setup
  - Validates configuration files exist
  - Obtains first SSL certificate via Cloudflare DNS
  - Sets proper file permissions

- **deploy.sh**: Automated deployment script
  - Checks prerequisites
  - Builds Docker images
  - Starts all services
  - Runs migrations
  - Collects static files
  - Creates superuser if needed

#### Documentation
- **DEPLOYMENT.md**: Comprehensive deployment guide
  - Prerequisites and requirements
  - Cloudflare setup instructions
  - Step-by-step deployment process
  - Maintenance procedures
  - Troubleshooting guide
  - Architecture diagram
  - Environment variable reference

#### Additional Files
- **.gitignore**: Updated with production-specific ignores
- **.dockerignore**: Optimized Docker build context
- **requirements.txt**: Added production dependencies
  - gunicorn==23.0.0
  - psycopg2-binary==2.9.10
  - redis==5.2.1
  - celery==5.4.0

### Key Features

1. **SSL/TLS Security**
   - Automated Let's Encrypt certificate generation
   - Cloudflare DNS-01 challenge for validation
   - Auto-renewal every 12 hours
   - Modern TLS configuration

2. **Production-Ready Infrastructure**
   - PostgreSQL for robust data persistence
   - Redis for caching and session storage
   - Celery for background task processing
   - Nginx as high-performance reverse proxy

3. **Security Hardening**
   - All secrets in environment variables
   - Non-root container users
   - HTTPS-only in production
   - Security headers (HSTS, XSS protection, etc.)
   - Secure cookie settings

4. **High Availability**
   - Health checks for all services
   - Automatic container restart
   - Connection pooling for database
   - Graceful degradation

5. **Developer Experience**
   - One-command deployment
   - Automated migrations
   - Comprehensive documentation
   - Easy local development with separate settings

### How to Deploy

1. **Prerequisites:**
   - Linux server with Docker and Docker Compose
   - Domain pointing to server IP (roommate.klauvi.is)
   - Cloudflare DNS management
   - Cloudflare API token with DNS edit permissions

2. **Configuration:**
   ```bash
   cp .env.prod.example .env.prod
   cp certbot/cloudflare.ini.example certbot/cloudflare.ini
   # Edit both files with your credentials
   ```

3. **Deploy:**
   ```bash
   chmod +x deploy.sh init-letsencrypt.sh
   ./deploy.sh
   ```

4. **Access:**
   - Application: https://roommate.klauvi.is
   - Admin: https://roommate.klauvi.is/admin/

### Technical Implementation

**Container Orchestration:**
- Docker Compose with named volumes for data persistence
- Bridge networking for inter-container communication
- Health checks ensure services are ready before dependent services start

**Database:**
- PostgreSQL with connection pooling (CONN_MAX_AGE: 600)
- Persistent volume for data
- Automated migrations on startup

**Caching & Sessions:**
- Redis-backed caching for improved performance
- Redis-backed sessions for scalability
- Password-protected Redis instance

**Background Tasks:**
- Celery worker for async task processing
- Celery beat for scheduled tasks
- Redis as message broker

**Web Server:**
- Gunicorn with 4 workers and 120s timeout
- Nginx reverse proxy with SSL termination
- Static file serving with 30-day cache
- Media file serving with 7-day cache

**SSL/TLS:**
- Let's Encrypt certificates via Certbot
- DNS-01 challenge using Cloudflare plugin
- Automatic renewal in background container
- TLS 1.2/1.3 only with secure ciphers

### Maintenance Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
git pull && docker-compose up -d --build

# Database backup
docker-compose exec db pg_dump -U roommate_user roommate > backup.sql

# Django management
docker-compose exec web python manage.py <command>
```

### Security Notes

- Never commit `.env.prod` or `certbot/cloudflare.ini` to version control
- Change the default admin password immediately after deployment
- Keep Docker images and Python packages updated
- Set up regular automated backups
- Monitor logs for suspicious activity

---

# Create admin page with user

Input:
```
create an authenticated admin site and one user that can authenticate, username=admin password=admin
add a profile section where the admin can change their password
```

What's Done
✅ Core Django App - Created with all necessary components
✅ Admin User - Username: admin, Password: admin
✅ Admin Site - Available at http://127.0.0.1:8000/admin/
✅ Profile Section - Available at http://127.0.0.1:8000/profile/

Features
Admin Login at /admin/ - Login with admin/admin
Profile Page at /profile/ - Shows user information and status
Change Password at /profile/password/ - Form to update password with validation
Success Confirmation - Shows success message after password change
How to Use
Visit http://127.0.0.1:8000/admin/
Login with:
Username: admin
Password: admin
Navigate to the Profile section using the navigation menu
Click "Change Password" to update your password
The development server is running in the background. All templates use Tailwind CSS for styling as per your project requirements.


# Player management

Input:
```
next i want to add an option to the admin section to add players. Fields for players should be:

name
phone
email
There should be a page that lists created players, and on that page there should be an option for each player to generate a roommate selector link. This will create a uuid and create a db record with that uuid and link it to the selected player. the roommate selector link should have the uuid as a query parameter
```

What's Been Created
Models
Player: Stores player information (name, phone, email) with UUID primary key
SelectionLink: Links a UUID to a player for roommate selection, tracks if it's been used
Views
PlayerListView: Displays all players with their selection links
PlayerCreateView: Form to add new players
GenerateSelectionLinkView: Creates/regenerates UUID selection links for players
Templates
player_list.html: Lists all players with:
Player details (name, phone, email)
Generated selection link with copy button
Generate/Regenerate link button for each player
player_form.html: Form to create new players
Features
Navigation: Added "Players" link to main navigation menu
Player Management: Add, list, and view players
Link Generation: Generate unique UUID-based selection links for each player
Copy to Clipboard: One-click copy functionality for selection links
Admin Integration: Players and SelectionLinks registered in Django admin
How to Use
Visit http://127.0.0.1:8000/players/
Click "Add Player" to create players
For each player, click "Generate Link" to create a unique roommate selection URL
The link format is: http://127.0.0.1:8000/select/?id=<uuid>
Click "Copy" to copy the link to clipboard
Links can be regenerated by clicking "Regenerate Link"
The selection links are ready to be used for the roommate selection form (which we'll implement next).


# Roommate select page

Input:
```
now create the select page. it should be open, no auth required. it should read the id query parameter, get the relevant player and greet them by name. they should see 3 dropdown lists with all the other player names, exclude the player making the selection. it should not be possible to select same name more than once. the form should only be valid when all 3 selections have been made. when the form is submitted, create a draft record in the database and generate a 2 digit random number that will be used to validate that the person submitting the form is correct by sending sms or email with the code, asking them to verify it. for now, you can just display the code on the verification page, we will handle sending it later
```

Roommate Selection Features
Selection Page (/select/?id=<uuid>)
No authentication required - Open to anyone with the link
Personalized greeting - "Halló [Player Name]!"
Dynamic dropdowns - 3 dropdown lists that:
Show all other players (excludes the current player)
Appear progressively (2nd appears after 1st selection, 3rd after 2nd)
Disable already-selected options to prevent duplicates
Submit button only enabled when all 3 selections are made
Verification Flow
Draft Creation - On form submission:

Creates a draft RoommateSelection record
Generates a random 2-digit verification code (10-99)
Stores all 3 roommate selections
Verification Page (/verify/?selection_id=<uuid>)

Displays the player's selections
Shows the verification code (in demo mode - ready for SMS/email integration)
Form to enter and validate the 2-digit code
Confirmation - After successful verification:

Updates selection status from "draft" to "verified"
Marks the selection link as used
Shows success page with final selections
Prevents reuse of the link
Additional Features
Duplicate Prevention - JavaScript prevents selecting the same player twice
Link Protection - Used links show a "Selection Already Complete" page
Validation - Server-side validation ensures all 3 selections are different and not the player themselves
Admin Integration - All selections visible in Django admin
How to Test
Visit http://127.0.0.1:8000/players/
Add a few test players
Generate a selection link for one player
Copy and visit the link (e.g., http://127.0.0.1:8000/select/?id=<uuid>)
Select 3 roommates
Submit and see the verification code displayed
Enter the code to verify
See the confirmation page
The system is now ready for SMS/email integration for sending verification codes!


# Admin Dashboard with Room Assignment Management

Input:
```
next i need a page for the admin to view all the selections. It should show statistics about number of players, how many links are unused, how many have been submitted, and any other relevant information you can think of. if all the links have been used and all players have been sent a link, try to create a suggestion for room pairing based on all the selections. The room pairing should be editable by the admin, and there should be a validate button that checks the current selection and reports if all players have been assigned to a room.
```

What's Been Created

**Models**
- `Room`: Manages room entities with name and finalization status
- `RoomAssignment`: Links players to rooms with UUID-based tracking

**Views**
- `DashboardView`: Main dashboard displaying comprehensive statistics and room assignments
- `GenerateRoomAssignmentsView`: Intelligent room pairing algorithm based on player preferences
- `UpdateRoomAssignmentView`: Edit existing room assignments
- `ValidateAssignmentsView`: Verify all players are assigned to rooms
- `DeleteRoomView`: Remove non-finalized rooms

**Dashboard Features**

Statistics Cards:
- Total Players count
- Selection Links (used/unused breakdown)
- Players with Links (shows deficit if any)
- Verified vs Draft selections

Room Assignment System:
- Automatic generation based on mutual preferences
- Smart algorithm prioritizing mutual roommate selections
- Editable room assignments via dropdown selectors
- Validation to ensure all players are assigned
- Delete rooms capability (for non-finalized only)

**Room Pairing Algorithm**

The system uses a sophisticated matching algorithm:
1. First Pass: Identifies groups with mutual preferences (all 3 players selected each other)
2. Second Pass: Assigns remaining players based on their top preferences
3. Ensures 3 players per room when possible
4. Handles edge cases with partial rooms

**Admin Capabilities**
- View comprehensive statistics at a glance
- Generate room assignments when all selections are complete
- Manually adjust room assignments via dropdown menus
- Validate that all players are assigned
- Delete and regenerate assignments as needed
- Track which rooms are finalized vs editable

**How to Use**

1. Visit http://127.0.0.1:8000/ (Dashboard is now the home page)
2. Review statistics to see selection progress
3. Once all players have verified selections, click "Generate Room Assignments"
4. Review generated room pairings (optimized for mutual preferences)
5. Manually adjust any room using the dropdown selectors
6. Click "Update Room" to save changes
7. Click "Validate Assignments" to verify all players are assigned
8. Delete and regenerate rooms as needed before finalizing

**Technical Implementation**
- Uses Django's prefetch_related for optimized queries
- Atomic transactions ensure data consistency
- Preference graph algorithm for optimal room matching
- Real-time validation feedback
- Non-finalized rooms can be edited/deleted
- All models registered in Django admin for manual override

**Navigation**
- Dashboard added as first menu item
- Accessible at root URL (/)
- Shows full statistics and room management interface


# Selections View with CSV Export

Input:
```
Add a new page for the admin to view the results of all selections with an option to export to csv
```

**What's Been Created**

**Views**
- `SelectionsView`: ListView displaying all roommate selections with statistics
- `ExportSelectionsView`: CSV export functionality for verified selections

**Templates**
- `selections.html`: Comprehensive table view of all selections with statistics cards

**Features**

**Selections Page** (`/selections/`)
- Complete table view of all player selections
- Displays player contact information (email, phone)
- Shows all 3 roommate choices with numbered badges
- Status badges (Verified/Draft) with color coding
- Timestamp for each submission
- Statistics cards showing:
  - Total selections count
  - Verified selections count
  - Draft selections count
- Pagination support (50 items per page)

**CSV Export**
- Export button prominently displayed at top of page
- Downloads as `roommate_selections.csv`
- Includes only verified selections
- Ordered by player name
- Contains columns:
  - Player Name
  - Player Email
  - Player Phone
  - First Choice
  - Second Choice
  - Third Choice
  - Status
  - Submitted At (formatted as YYYY-MM-DD HH:MM:SS)

**Navigation**
- "Selections" link added to main navigation menu
- Positioned between "Players" and "Admin"

**How to Use**

1. Visit http://127.0.0.1:8000/selections/
2. View all player selections in a comprehensive table
3. Review statistics at a glance with the statistics cards
4. Click "Export to CSV" to download all verified selections
5. Open CSV file in Excel, Google Sheets, or any spreadsheet application
6. Use exported data for record-keeping or external processing

**Technical Implementation**
- Uses `select_related` for optimized database queries
- CSV writer from Python's standard library
- Pagination for large datasets
- Status filtering to separate verified from draft selections
- Responsive table design with Tailwind CSS
- Download triggered with proper HTTP headers for file attachment

