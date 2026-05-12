-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Guest Profiles (Unified across channels)
CREATE TABLE guests (
    guest_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Reservations
CREATE TABLE reservations (
    reservation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guest_id UUID REFERENCES guests(guest_id) ON DELETE CASCADE,
    booking_ref VARCHAR(100) UNIQUE NOT NULL,
    property_id VARCHAR(100) NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed'
);

-- 3. Conversations (Linking channels and reservations)
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guest_id UUID REFERENCES guests(guest_id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES reservations(reservation_id) ON DELETE SET NULL,
    channel_source VARCHAR(50) NOT NULL, -- e.g., 'whatsapp', 'airbnb'
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Messages (Unified tracking)
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    sender_type VARCHAR(50) NOT NULL, -- 'guest', 'agent', 'ai'
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- AI Tracking metadata (nullable for guest messages)
    query_type VARCHAR(50),
    confidence_score DECIMAL(3,2),
    is_ai_drafted BOOLEAN DEFAULT FALSE,
    was_agent_edited BOOLEAN DEFAULT FALSE,
    was_auto_sent BOOLEAN DEFAULT FALSE
);

/*
DESIGN DECISIONS & THE HARDEST DECISION:
The hardest design decision was determining how to link a generic inbound message (which only has a channel source and name) to a unified `guest_id` and a specific `reservation_id`. 

I chose to abstract the connection through a `conversations` table. This allows a guest to message us via WhatsApp today and Airbnb tomorrow. The application layer handles the identity resolution (e.g., matching a WhatsApp phone number to an existing guest profile) and links that specific channel's `conversation` to the overarching `guest_id` and active `reservation_id`. The `messages` table itself remains pure and simply logs the chronological flow, keeping the schema normalized and highly scalable.
*/