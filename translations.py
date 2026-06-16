"""
translations.py — Santosh E-Dairy
Single source of truth for ALL UI strings in English and Nepali.

Usage:
    from translations import t
    label = t("save")           # returns "सुरक्षित गर्नुस्" (if lang=NE)

Adding a new string:
    1. Add a key here in both EN and NE.
    2. Call t("your_key") in the UI. Never hardcode strings in UI files.
"""

# ── Navigation ─────────────────────────────────────────────────────────────────
NAV = {
    "dashboard":            {"EN": "Dashboard",             "NE": "ड्यासबोर्ड"},
    "milk_collection":      {"EN": "Milk Collection",       "NE": "दूध संकलन"},
    "product_transaction":  {"EN": "Product Transaction",   "NE": "उत्पादन कारोबार"},
    "payments":             {"EN": "Payments",              "NE": "भुक्तानी"},
    "inventory":            {"EN": "Inventory",             "NE": "मौजदात"},
    "reports":              {"EN": "रिपोर्ट",              "NE": "रिपोर्ट"},
    "farmers":              {"EN": "Farmers",               "NE": "किसानहरू"},
    "settings":             {"EN": "Settings",              "NE": "सेटिङ"},
    "navigation":           {"EN": "NAVIGATION",            "NE": "नेभिगेसन"},
    "lock_screen":          {"EN": "Lock Screen",           "NE": "स्क्रिन लक गर्नुस्"},
}

# ── Common actions ─────────────────────────────────────────────────────────────
ACTIONS = {
    "save":                 {"EN": "Save",                  "NE": "सुरक्षित गर्नुस्"},
    "cancel":               {"EN": "Cancel",                "NE": "रद्द गर्नुस्"},
    "edit":                 {"EN": "Edit",                  "NE": "सम्पादन"},
    "delete":               {"EN": "Delete",                "NE": "मेट्नुस्"},
    "search":               {"EN": "Search",                "NE": "खोज्नुस्"},
    "clear":                {"EN": "Clear",                 "NE": "खाली गर्नुस्"},
    "back":                 {"EN": "Back",                  "NE": "पछाडि"},
    "close":                {"EN": "Close",                 "NE": "बन्द गर्नुस्"},
    "confirm":              {"EN": "Confirm",               "NE": "पुष्टि गर्नुस्"},
    "print":                {"EN": "Print",                 "NE": "छाप्नुस्"},
    "export_pdf":           {"EN": "Export PDF",            "NE": "PDF निर्यात"},
    "export_excel":         {"EN": "Export Excel",          "NE": "Excel निर्यात"},
    "preview":              {"EN": "Preview",               "NE": "पूर्वावलोकन"},
    "add":                  {"EN": "Add",                   "NE": "थप्नुस्"},
    "deactivate":           {"EN": "Deactivate",            "NE": "निष्क्रिय गर्नुस्"},
    "activate":             {"EN": "Activate",              "NE": "सक्रिय गर्नुस्"},
    "yes":                  {"EN": "Yes",                   "NE": "हो"},
    "no":                   {"EN": "No",                    "NE": "होइन"},
    "ok":                   {"EN": "OK",                    "NE": "ठिक छ"},
    "login":                {"EN": "Login",                 "NE": "लगिन"},
    "logout":               {"EN": "Logout",                "NE": "लगआउट"},
}

# ── Dashboard ──────────────────────────────────────────────────────────────────
DASHBOARD = {
    "dashboard_title":      {"EN": "Dashboard",             "NE": "ड्यासबोर्ड"},
    "today_milk":           {"EN": "Today's Milk",          "NE": "आजको दूध"},
    "today_collection":     {"EN": "Today's Collection",    "NE": "आजको संकलन"},
    "outstanding_balance":  {"EN": "Outstanding Balance",   "NE": "बाँकी रकम"},
    "products_in_stock":    {"EN": "Products in Stock",     "NE": "स्टकमा उत्पादन"},
    "transactions_today":   {"EN": "Transactions Today",    "NE": "आजका कारोबार"},
    "quick_actions":        {"EN": "Quick Actions",         "NE": "द्रुत कार्यहरू"},
    "recent_transactions":  {"EN": "Recent Transactions",   "NE": "भर्खरका कारोबार"},
    "backup_ok":            {"EN": "✓ Backup OK",           "NE": "✓ ब्याकअप ठिक"},
    "backup_warning":       {"EN": "⚠ Backup Overdue",      "NE": "⚠ ब्याकअप बाँकी"},
}

# ── Login & Auth ───────────────────────────────────────────────────────────────
AUTH = {
    "password":             {"EN": "PASSWORD",              "NE": "पासवर्ड"},
    "enter_password":       {"EN": "Enter password",        "NE": "पासवर्ड लेख्नुस्"},
    "login_btn":            {"EN": "Login",                 "NE": "लगिन"},
    "invalid_password":     {"EN": "Invalid password.",     "NE": "पासवर्ड गलत छ।"},
    "enter_password_first": {"EN": "Please enter your password.", "NE": "कृपया पासवर्ड लेख्नुस्।"},
    "account_unlocked":     {"EN": "Account unlocked. You may try again.",
                             "NE": "खाता अनलक भयो। पुनः प्रयास गर्नुस्।"},
    "locked_countdown":     {"EN": "Account locked. Try again in {m}m {s:02d}s.",
                             "NE": "खाता लक भयो। {m}मि {s:02d}से पछि प्रयास गर्नुस्।"},
    # Change password dialog
    "change_password":      {"EN": "Change Password",       "NE": "पासवर्ड परिवर्तन"},
    "set_password":         {"EN": "Set Your Password",     "NE": "पासवर्ड सेट गर्नुस्"},
    "forced_intro":         {"EN": "You are logging in with the default password.\nYou must set a new password before continuing.",
                             "NE": "तपाईं पूर्वनिर्धारित पासवर्डले लगिन गर्दै हुनुहुन्छ।\nजारी राख्नु अघि नयाँ पासवर्ड सेट गर्नु आवश्यक छ।"},
    "voluntary_intro":      {"EN": "Enter your current password and choose a new one.",
                             "NE": "हालको पासवर्ड र नयाँ पासवर्ड लेख्नुस्।"},
    "current_password":     {"EN": "CURRENT PASSWORD",      "NE": "हालको पासवर्ड"},
    "new_password":         {"EN": "NEW PASSWORD",          "NE": "नयाँ पासवर्ड"},
    "confirm_password":     {"EN": "CONFIRM NEW PASSWORD",  "NE": "नयाँ पासवर्ड पुष्टि"},
    "enter_current_pw":     {"EN": "Enter current password","NE": "हालको पासवर्ड लेख्नुस्"},
    "min_6_chars":          {"EN": "At least 6 characters", "NE": "कम्तीमा ६ अक्षर"},
    "repeat_new_pw":        {"EN": "Repeat new password",   "NE": "नयाँ पासवर्ड दोहोर्याउनुस्"},
    "all_fields_required":  {"EN": "All fields are required.","NE": "सबै फिल्ड आवश्यक छ।"},
    "pw_changed_ok":        {"EN": "✓ Password changed successfully.",
                             "NE": "✓ पासवर्ड सफलतापूर्वक परिवर्तन भयो।"},
    "pw_no_match":          {"EN": "New passwords do not match.",
                             "NE": "नयाँ पासवर्ड मेल खाएन।"},
    "pw_too_short":         {"EN": "New password must be at least 6 characters.",
                             "NE": "नयाँ पासवर्ड कम्तीमा ६ अक्षर हुनुपर्छ।"},
    "pw_default_reuse":     {"EN": "You cannot use the default password. Please choose a unique password.",
                             "NE": "पूर्वनिर्धारित पासवर्ड प्रयोग गर्न मिल्दैन। नयाँ पासवर्ड छान्नुस्।"},
    "set_password_btn":     {"EN": "Set Password",          "NE": "पासवर्ड सेट गर्नुस्"},
    "change_password_btn":  {"EN": "Change Password",       "NE": "पासवर्ड परिवर्तन गर्नुस्"},
}

# ── Farmer Management ──────────────────────────────────────────────────────────
FARMERS = {
    "farmer_management":    {"EN": "Farmer Management",     "NE": "किसान व्यवस्थापन"},
    "farmer_list":          {"EN": "Farmer List",           "NE": "किसान सूची"},
    "add_farmer":           {"EN": "Add Farmer",            "NE": "किसान थप्नुस्"},
    "edit_farmer":          {"EN": "Edit Farmer",           "NE": "किसान सम्पादन"},
    "deactivate_farmer":    {"EN": "Deactivate Farmer",     "NE": "किसान निष्क्रिय गर्नुस्"},
    "farmer_code":          {"EN": "Farmer Code",           "NE": "किसान कोड"},
    "farmer_name_en":       {"EN": "Name (English)",        "NE": "नाम (अंग्रेजी)"},
    "farmer_name_ne":       {"EN": "Name (Nepali)",         "NE": "नाम (नेपाली)"},
    "phone":                {"EN": "Phone",                 "NE": "फोन"},
    "address":              {"EN": "Address",               "NE": "ठेगाना"},
    "status":               {"EN": "Status",                "NE": "स्थिति"},
    "active":               {"EN": "Active",                "NE": "सक्रिय"},
    "inactive":             {"EN": "Inactive",              "NE": "निष्क्रिय"},
    "search_placeholder":   {"EN": "Search by code, name or phone...",
                             "NE": "कोड, नाम वा फोनले खोज्नुस्..."},
    "farmer_saved":         {"EN": "Farmer saved successfully.",
                             "NE": "किसान सफलतापूर्वक सुरक्षित गरियो।"},
    "farmer_updated":       {"EN": "Farmer updated successfully.",
                             "NE": "किसान सफलतापूर्वक अद्यावधिक गरियो।"},
    "farmer_deactivated":   {"EN": "Farmer deactivated.",  "NE": "किसान निष्क्रिय गरियो।"},
    "farmer_activated":     {"EN": "Farmer activated.",     "NE": "किसान सक्रिय गरियो।"},
    "code_required":        {"EN": "Farmer Code is required.",
                             "NE": "किसान कोड आवश्यक छ।"},
    "name_required":        {"EN": "Farmer name is required.",
                             "NE": "किसानको नाम आवश्यक छ।"},
    "code_exists":          {"EN": "Farmer Code already exists.",
                             "NE": "किसान कोड पहिले नै छ।"},
    "deactivate_balance":   {"EN": "Cannot deactivate. Farmer has outstanding balance of NPR {amount}.",
                             "NE": "निष्क्रिय गर्न सकिँदैन। किसानको NPR {amount} बाँकी छ।"},
    "confirm_deactivate":   {"EN": "Are you sure you want to deactivate this farmer?",
                             "NE": "के तपाईं यो किसानलाई निष्क्रिय गर्न निश्चित हुनुहुन्छ?"},
    "no_farmers":           {"EN": "No farmers found.",     "NE": "कुनै किसान भेटिएन।"},
    # Table headers
    "col_code":             {"EN": "Code",                  "NE": "कोड"},
    "col_name":             {"EN": "Name",                  "NE": "नाम"},
    "col_phone":            {"EN": "Phone",                 "NE": "फोन"},
    "col_address":          {"EN": "Address",               "NE": "ठेगाना"},
    "col_status":           {"EN": "Status",                "NE": "स्थिति"},
    "col_actions":          {"EN": "Actions",               "NE": "कार्यहरू"},
}

# ── Milk Collection ────────────────────────────────────────────────────────────
MILK = {
    "milk_collection":      {"EN": "Milk Collection",       "NE": "दूध संकलन"},
    "farmer_id_prompt":     {"EN": "Enter Farmer Code",     "NE": "किसान कोड लेख्नुस्"},
    "session":              {"EN": "Session",               "NE": "सत्र"},
    "morning":              {"EN": "Morning",               "NE": "बिहान"},
    "evening":              {"EN": "Evening",               "NE": "बेलुका"},
    "milk_type":            {"EN": "Milk Type",             "NE": "दूधको प्रकार"},
    "cow":                  {"EN": "Cow",                   "NE": "गाई"},
    "buffalo":              {"EN": "Buffalo",               "NE": "भैँसी"},
    "quantity":             {"EN": "Quantity (Liter)",      "NE": "परिमाण (लिटर)"},
    "fat":                  {"EN": "FAT (%)",               "NE": "फ्याट (%)"},
    "snf":                  {"EN": "SNF (%)",               "NE": "SNF (%)"},
    "rate":                 {"EN": "Rate (NPR/Liter)",      "NE": "दर (NPR/लिटर)"},
    "amount":               {"EN": "Amount (NPR)",          "NE": "रकम (NPR)"},
    "date":                 {"EN": "Date",                  "NE": "मिति"},
    "cancel_transaction":   {"EN": "Cancel Transaction",    "NE": "कारोबार रद्द गर्नुस्"},
    "duplicate_entry":      {"EN": "Milk collection already exists for this farmer and session.",
                             "NE": "यस किसान र सत्रको लागि दूध संकलन पहिले नै छ।"},
    "farmer_not_found":     {"EN": "Farmer not found.",     "NE": "किसान भेटिएन।"},
    "farmer_inactive":      {"EN": "This farmer is inactive.",
                             "NE": "यो किसान निष्क्रिय छ।"},
    "qty_invalid":          {"EN": "Quantity must be greater than zero.",
                             "NE": "परिमाण शून्यभन्दा बढी हुनुपर्छ।"},
    "fat_invalid":          {"EN": "FAT value must be 0 or greater.",
                             "NE": "फ्याट मान शून्य वा बढी हुनुपर्छ।"},
    "snf_invalid":          {"EN": "SNF value must be 0 or greater.",
                             "NE": "SNF मान शून्य वा बढी हुनुपर्छ।"},
    "milk_saved":           {"EN": "Milk collection saved.",
                             "NE": "दूध संकलन सुरक्षित गरियो।"},
    "cancellation_reason":  {"EN": "Cancellation Reason",  "NE": "रद्द गर्नुको कारण"},
    "reason_required":      {"EN": "Please enter a reason for cancellation.",
                             "NE": "कृपया रद्द गर्नुको कारण लेख्नुस्।"},
    "confirm_cancel_txn":   {"EN": "Are you sure you want to cancel this transaction? This cannot be undone.",
                             "NE": "के तपाईं यो कारोबार रद्द गर्न निश्चित हुनुहुन्छ? यो पूर्ववत हुन सक्दैन।"},
}

# ── Product Management ─────────────────────────────────────────────────────────
PRODUCT_MGMT = {
    "product_management":    {"EN": "Product Management",    "NE": "उत्पादन व्यवस्थापन"},
    "product_list":          {"EN": "Product List",          "NE": "उत्पादन सूची"},
    "add_product":           {"EN": "Add Product",           "NE": "उत्पादन थप्नुस्"},
    "edit_product":          {"EN": "Edit Product",          "NE": "उत्पादन सम्पादन"},
    "product_name_en":       {"EN": "Name (English)",        "NE": "नाम (अंग्रेजी)"},
    "product_name_ne":       {"EN": "Name (Nepali)",         "NE": "नाम (नेपाली)"},
    "unit_label":            {"EN": "Unit",                  "NE": "इकाई"},
    "unit_liter":            {"EN": "Liter",                 "NE": "लिटर"},
    "unit_kg":               {"EN": "KG",                   "NE": "केजी"},
    "default_rate_label":    {"EN": "Default Rate (NPR)",    "NE": "पूर्वनिर्धारित दर (NPR)"},
    "default_rate_hint":     {"EN": "Pre-filled on transaction screen.",
                              "NE": "कारोबार स्क्रिनमा स्वतः भरिन्छ।"},
    "is_milk_label":         {"EN": "Product Type",          "NE": "उत्पादन प्रकार"},
    "is_milk_yes":           {"EN": "Milk Product",          "NE": "दूध उत्पादन"},
    "is_milk_no":            {"EN": "Other Product",         "NE": "अन्य उत्पादन"},
    "product_saved":         {"EN": "Product saved successfully.",
                              "NE": "उत्पादन सफलतापूर्वक सुरक्षित गरियो।"},
    "product_updated":       {"EN": "Product updated successfully.",
                              "NE": "उत्पादन सफलतापूर्वक अद्यावधिक गरियो।"},
    "product_name_required": {"EN": "Product name (English) is required.",
                              "NE": "उत्पादनको नाम (अंग्रेजी) आवश्यक छ।"},
    "product_name_exists":   {"EN": "A product with this English name already exists.",
                              "NE": "यस अंग्रेजी नामको उत्पादन पहिले नै छ।"},
    "default_rate_invalid":  {"EN": "Default rate must be zero or a positive number.",
                              "NE": "पूर्वनिर्धारित दर शून्य वा धनात्मक संख्या हुनुपर्छ।"},
    "milk_unit_fixed":       {"EN": "Milk unit is fixed as LITER and cannot be changed.",
                              "NE": "दूधको इकाई LITER मा निर्धारित छ र परिवर्तन गर्न सकिँदैन।"},
    "no_products":           {"EN": "No products found.",    "NE": "कुनै उत्पादन भेटिएन।"},
    "col_product_name":      {"EN": "Product Name",          "NE": "उत्पादनको नाम"},
    "col_default_rate":      {"EN": "Default Rate",          "NE": "पूर्वनिर्धारित दर"},
    "col_is_milk":           {"EN": "Type",                  "NE": "प्रकार"},
    "milk_type_label":       {"EN": "Milk",                  "NE": "दूध"},
    "other_type_label":      {"EN": "Other",                 "NE": "अन्य"},
    "ph_product_management": {"EN": "Phase 5",               "NE": "चरण ५"},
}

# ── Product Transaction ────────────────────────────────────────────────────────
PRODUCT_TXN = {
    "product_transaction":  {"EN": "Product Transaction",   "NE": "उत्पादन कारोबार"},
    "product":              {"EN": "Product",               "NE": "उत्पादन"},
    "select_product":       {"EN": "Select Product",        "NE": "उत्पादन छान्नुस्"},
    "quantity_kg":          {"EN": "Quantity (KG)",         "NE": "परिमाण (केजी)"},
    "rate_per_kg":          {"EN": "Rate (NPR/KG)",         "NE": "दर (NPR/केजी)"},
    "remarks":              {"EN": "Remarks",               "NE": "टिप्पणी"},
    "txn_saved":            {"EN": "Transaction saved.",    "NE": "कारोबार सुरक्षित गरियो।"},
}

# ── Payments ───────────────────────────────────────────────────────────────────
PAYMENTS = {
    "payment_entry":        {"EN": "Record Payment",        "NE": "भुक्तानी दर्ता"},
    "payment_date":         {"EN": "Payment Date",          "NE": "भुक्तानी मिति"},
    "amount_paid":          {"EN": "Amount Paid (NPR)",     "NE": "तिरेको रकम (NPR)"},
    "outstanding":          {"EN": "Outstanding Balance",   "NE": "बाँकी रकम"},
    "receipt_number":       {"EN": "Receipt No.",           "NE": "रसिद नं."},
    "print_receipt":        {"EN": "Print Receipt",         "NE": "रसिद छाप्नुस्"},
    "payment_saved":        {"EN": "Payment recorded.",     "NE": "भुक्तानी दर्ता गरियो।"},
    "overpayment":          {"EN": "Payment amount exceeds outstanding balance.",
                             "NE": "भुक्तानी रकम बाँकी रकमभन्दा बढी छ।"},
    "zero_payment":         {"EN": "Payment amount must be greater than zero.",
                             "NE": "भुक्तानी रकम शून्यभन्दा बढी हुनुपर्छ।"},
    "zero_balance":         {"EN": "This farmer has no outstanding balance.",
                             "NE": "यस किसानको कुनै बाँकी रकम छैन।"},
}

# ── Inventory ──────────────────────────────────────────────────────────────────
INVENTORY = {
    "inventory":            {"EN": "Inventory",             "NE": "मौजदात"},
    "stock_in":             {"EN": "Stock In",              "NE": "स्टक भित्र्याउनुस्"},
    "stock_out":            {"EN": "Stock Out",             "NE": "स्टक बाहिर्याउनुस्"},
    "current_stock":        {"EN": "Current Stock",         "NE": "हालको स्टक"},
    "view_history":         {"EN": "View History",          "NE": "इतिहास हेर्नुस्"},
    "movement_type":        {"EN": "Movement Type",         "NE": "आवागमन प्रकार"},
    "notes":                {"EN": "Notes",                 "NE": "नोट"},
    "stock_saved":          {"EN": "Stock movement saved.", "NE": "स्टक आवागमन सुरक्षित गरियो।"},
    "insufficient_stock":   {"EN": "Insufficient stock. Current stock: {qty} {unit}.",
                             "NE": "अपर्याप्त स्टक। हालको स्टक: {qty} {unit}।"},
    "qty_zero":             {"EN": "Quantity must be greater than zero.",
                             "NE": "परिमाण शून्यभन्दा बढी हुनुपर्छ।"},
}

# ── Reports ────────────────────────────────────────────────────────────────────
REPORTS = {
    "reports":              {"EN": "Reports",               "NE": "रिपोर्टहरू"},
    "daily_collection":     {"EN": "Daily Milk Collection", "NE": "दैनिक दूध संकलन"},
    "farmer_statement":     {"EN": "Farmer Statement",      "NE": "किसान विवरण"},
    "payment_report":       {"EN": "Payment Report",        "NE": "भुक्तानी रिपोर्ट"},
    "outstanding_report":   {"EN": "Outstanding Balance",   "NE": "बाँकी रकम रिपोर्ट"},
    "inventory_report":     {"EN": "Inventory Report",      "NE": "मौजदात रिपोर्ट"},
    "product_txn_report":   {"EN": "Product Transaction",   "NE": "उत्पादन कारोबार रिपोर्ट"},
    "monthly_summary":      {"EN": "Monthly Summary",       "NE": "मासिक सारांश"},
    "from_date":            {"EN": "From Date",             "NE": "मिति देखि"},
    "to_date":              {"EN": "To Date",               "NE": "मिति सम्म"},
    "all_time":             {"EN": "All Time",              "NE": "सबै समय"},
    "date_range":           {"EN": "Date Range",            "NE": "मिति दायरा"},
    "grand_total":          {"EN": "Grand Total",           "NE": "जम्मा"},
    "total_paid":           {"EN": "Total Paid",            "NE": "जम्मा तिरेको"},
    "balance":              {"EN": "Balance",               "NE": "बाँकी"},
    "opening_balance":      {"EN": "Opening Balance",       "NE": "सुरुको बाँकी"},
    "closing_balance":      {"EN": "Closing Balance",       "NE": "अन्तिम बाँकी"},
    "no_data":              {"EN": "No data for selected period.",
                             "NE": "चयन गरिएको अवधिको लागि कुनै डाटा छैन।"},
}

# ── Settings ───────────────────────────────────────────────────────────────────
SETTINGS = {
    "settings":             {"EN": "Settings",              "NE": "सेटिङ"},
    "org_info":             {"EN": "Organisation Information","NE": "संस्था जानकारी"},
    "org_name_en":          {"EN": "Name (English)",        "NE": "नाम (अंग्रेजी)"},
    "org_name_ne":          {"EN": "Name (Nepali)",         "NE": "नाम (नेपाली)"},
    "org_address_en":       {"EN": "Address (English)",     "NE": "ठेगाना (अंग्रेजी)"},
    "org_address_ne":       {"EN": "Address (Nepali)",      "NE": "ठेगाना (नेपाली)"},
    "org_phone":            {"EN": "Phone",                 "NE": "फोन"},
    "org_logo":             {"EN": "Logo",                  "NE": "लोगो"},
    "pricing_formula":      {"EN": "Pricing Formula",       "NE": "मूल्य सूत्र"},
    "formula_hint":         {"EN": "e.g. (fat*8)+(snf*4)", "NE": "उदा. (fat*8)+(snf*4)"},
    "formula_saved":        {"EN": "Formula saved.",        "NE": "सूत्र सुरक्षित गरियो।"},
    "formula_invalid":      {"EN": "Invalid formula. Please check and try again.",
                             "NE": "सूत्र गलत छ। जाँच गरी पुनः प्रयास गर्नुस्।"},
    "backup_settings":      {"EN": "Backup Settings",       "NE": "ब्याकअप सेटिङ"},
    "backup_folder":        {"EN": "Backup Folder",         "NE": "ब्याकअप फोल्डर"},
    "backup_now":           {"EN": "Backup Now",            "NE": "अहिले ब्याकअप गर्नुस्"},
    "restore_backup":       {"EN": "Restore Backup",        "NE": "ब्याकअप पुनःस्थापना"},
    "backup_success":       {"EN": "Backup created successfully.",
                             "NE": "ब्याकअप सफलतापूर्वक सिर्जना भयो।"},
    "backup_failed":        {"EN": "Backup failed. Check backup location.",
                             "NE": "ब्याकअप असफल भयो। ब्याकअप स्थान जाँच्नुस्।"},
    "password_section":     {"EN": "Password Management",  "NE": "पासवर्ड व्यवस्थापन"},
    "language":             {"EN": "Language",              "NE": "भाषा"},
    "language_english":     {"EN": "English",               "NE": "अंग्रेजी"},
    "language_nepali":      {"EN": "Nepali (नेपाली)",       "NE": "नेपाली"},
    "idle_timeout":         {"EN": "Idle Lock (minutes)",   "NE": "निष्क्रिय लक (मिनेट)"},
    "settings_saved":       {"EN": "Settings saved.",       "NE": "सेटिङ सुरक्षित गरियो।"},
    "browse":               {"EN": "Browse...",             "NE": "खोज्नुस्..."},
    "choose_logo":          {"EN": "Choose Logo",           "NE": "लोगो छान्नुस्"},
}

# ── Common table columns ───────────────────────────────────────────────────────
TABLE = {
    "col_date":             {"EN": "Date",                  "NE": "मिति"},
    "col_farmer":           {"EN": "Farmer",                "NE": "किसान"},
    "col_product":          {"EN": "Product",               "NE": "उत्पादन"},
    "col_quantity":         {"EN": "Quantity",              "NE": "परिमाण"},
    "col_rate":             {"EN": "Rate",                  "NE": "दर"},
    "col_amount":           {"EN": "Amount (NPR)",          "NE": "रकम (NPR)"},
    "col_status":           {"EN": "Status",                "NE": "स्थिति"},
    "col_session":          {"EN": "Session",               "NE": "सत्र"},
    "col_fat":              {"EN": "FAT",                   "NE": "फ्याट"},
    "col_snf":              {"EN": "SNF",                   "NE": "SNF"},
    "col_type":             {"EN": "Type",                  "NE": "प्रकार"},
    "col_notes":            {"EN": "Notes",                 "NE": "नोट"},
    "col_receipt":          {"EN": "Receipt No.",           "NE": "रसिद नं."},
    "col_unit":             {"EN": "Unit",                  "NE": "इकाई"},
}

# ── Status bar ─────────────────────────────────────────────────────────────────
STATUS = {
    "db_connected":         {"EN": "● Database Connected",  "NE": "● डाटाबेस जोडिएको"},
    "version":              {"EN": "Santosh E-Dairy",       "NE": "सन्तोष इ-डेरी"},
}

# ── Error / generic messages ───────────────────────────────────────────────────
MESSAGES = {
    "error":                {"EN": "Error",                 "NE": "त्रुटि"},
    "success":              {"EN": "Success",               "NE": "सफल"},
    "warning":              {"EN": "Warning",               "NE": "चेतावनी"},
    "confirm":              {"EN": "Confirm",               "NE": "पुष्टि"},
    "coming_soon":          {"EN": "Coming Soon",           "NE": "छिट्टै आउँदैछ"},
    "welcome":              {"EN": "Welcome to Santosh E-Dairy",
                             "NE": "सन्तोष इ-डेरीमा स्वागत छ"},
    "db_created":           {"EN": "Database created successfully.",
                             "NE": "डाटाबेस सफलतापूर्वक सिर्जना भयो।"},
    "unexpected_error":     {"EN": "Unexpected error: {err}",
                             "NE": "अप्रत्याशित त्रुटि: {err}"},
    "placeholder_hint":     {"EN": "This module will be built in the next development phase.",
                             "NE": "यो मोड्युल अर्को विकास चरणमा बनाइनेछ।"},
}

# ── Placeholders ───────────────────────────────────────────────────────────────
PLACEHOLDERS = {
    "ph_milk_collection":      {"EN": "Phase 6 — Coming Soon", "NE": "चरण ६ — छिट्टै"},
    "ph_product_transaction":  {"EN": "Phase 7 — Coming Soon", "NE": "चरण ७ — छिट्टै"},
    "ph_payments":             {"EN": "Phase 8 — Coming Soon", "NE": "चरण ८ — छिट्टै"},
    "ph_inventory":            {"EN": "Phase 9 — Coming Soon", "NE": "चरण ९ — छिट्टै"},
    "ph_reports":              {"EN": "Phase 12 — Coming Soon","NE": "चरण १२ — छिट्टै"},
    "ph_farmers":              {"EN": "Phase 4 — Coming Soon", "NE": "चरण ४ — छिट्टै"},
    "ph_settings":             {"EN": "Phase 10 — Coming Soon","NE": "चरण १० — छिट्टै"},
    "ph_products":             {"EN": "Phase 5",               "NE": "चरण ५"},
}

# ══════════════════════════════════════════════════════════════════════════════
# Master dictionary — merge all sections
# ══════════════════════════════════════════════════════════════════════════════
_ALL: dict[str, dict[str, str]] = {}
for _section in [
    NAV, ACTIONS, DASHBOARD, AUTH, FARMERS, MILK,
    PRODUCT_MGMT, PRODUCT_TXN, PAYMENTS, INVENTORY, REPORTS,
    SETTINGS, TABLE, STATUS, MESSAGES, PLACEHOLDERS,
]:
    _ALL.update(_section)


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════
def t(key: str, **kwargs) -> str:
    """
    Return the translated string for key in the current app language.
    Falls back to English if the Nepali string is missing.
    Supports format placeholders: t("locked_countdown", m=4, s=30)
    """
    from database.database import get_setting
    lang = get_setting("default_language", "NE")
    if lang not in ("EN", "NE"):
        lang = "NE"

    entry = _ALL.get(key)
    if entry is None:
        return key   # return raw key so missing translations are obvious

    text = entry.get(lang) or entry.get("EN") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def set_language(lang: str) -> None:
    """Set app language. lang must be 'EN' or 'NE'."""
    from database.database import set_setting
    if lang in ("EN", "NE"):
        set_setting("default_language", lang)


def all_keys() -> list[str]:
    """Return all translation keys (for testing completeness)."""
    return list(_ALL.keys())
