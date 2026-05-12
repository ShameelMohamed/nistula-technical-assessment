# Question A — The Immediate Response

## Response

> "Hi there. I am incredibly sorry to hear about the hot water issue at this hour, especially with your guests arriving so soon. I have immediately flagged this as an urgent priority for our on-call caretaker, who will be at the property to assist. Our management team will review your refund request first thing in the morning."

## Why

At 3:00 AM, guests need empathy and immediate action. The AI should not promise a definitive refund (protecting the business) but must:

- Acknowledge the frustration
- Validate the urgency and time pressure
- Clearly communicate the next physical action (caretaker dispatched)

This balances customer experience with operational responsibility.

---

# Question B — The System Design

## 1. Trigger

The webhook receives the guest message.  
The AI classifies the message as:

```text
query_type: complaint
action: escalate
```

This immediately bypasses automated resolution flows.

---

## 2. Notification Layer

A high-priority alert is triggered through systems such as:

- Twilio
- PagerDuty
- SMS / automated phone call routing

The notification is sent directly to:

- The on-call caretaker
- The property manager on duty

---

## 3. Logging & Persistence

The database records:

```text
query_type: complaint
status: critical
priority: urgent
```

The full conversation history is preserved for auditing and operational follow-up.

---

## 4. Operations Dashboard

The Nistula operations dashboard surfaces the issue prominently by:

- Highlighting the ticket in red
- Pinning the issue to the top of the active queue
- Displaying escalation timers and acknowledgement state

---

## 5. Fail-safe Escalation

If no human agent acknowledges the issue within 30 minutes:

```text
3:00 AM → Initial escalation
3:30 AM → Secondary escalation triggered
```

The system automatically routes the alert to the Regional Director or senior escalation contact to ensure accountability.

---

# Question C — The Learning

This pattern suggests a systemic infrastructure issue rather than a one-off anomaly.

Possible causes include:

- A failing geyser heating element
- Electrical instability
- Localized power fluctuations
- Maintenance neglect over time

---

## What the System Should Do

The analytics layer should automatically detect repeated operational failures using anomaly thresholds.

Example rule:

```text
Entity: Villa B1
Tag: complaint
Issue: hot water
Threshold: >2 incidents within 60 days
```

Once the threshold is exceeded, the system should:

- Flag the property for maintenance review
- Notify operations management
- Generate an internal reliability alert

---

## What I Would Build

I would implement a preventative IoT monitoring layer.

### Proposed Architecture

Install lightweight local-first sensors on water heaters to monitor:

- Temperature consistency
- Heating efficiency
- Current draw / electrical behavior
- Runtime anomalies

### Result

The platform could proactively detect degradation before guest impact occurs and automatically create maintenance tickets ahead of check-ins.

This shifts the business model from:

```text
Reactive support → Proactive infrastructure maintenance
```

Reducing refunds, operational emergencies, and negative guest experiences.
