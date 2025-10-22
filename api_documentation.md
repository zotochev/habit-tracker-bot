### Overview
This API powers a habit-tracking backend with habits, scheduled notifications, and completion events. Notifications belong to habits; events are created only for notifications. Dates/times are generally ISO 8601 unless otherwise noted.

- Base path: `/v1`
- Routers: `/habits`, `/notifications` (plus `/auth`, `/users`, not covered here)

---

### Models (Schemas)

#### HabitBase
- `name: string`
- `description: string | null`
- `start_date: date`
- `end_date: date | null`
- `times_per_day: int` (>= 1)
- `repeat_type: "daily" | "weekly" | "monthly"`
- `days_mask: int` (bitmask of active days)
  - daily: ignored (treated as every day)
  - weekly: bits 0..6 for Mon..Sun
  - monthly: bits 0..30 for days 1..31

#### HabitCreate extends HabitBase
- `user_id: int`

#### HabitUpdate extends HabitBase
- `id: int`
- `user_id: int`
- All HabitBase fields optional for patching

#### Habit extends HabitBase
- `id: int`
- `user_id: int`
- `created_at: datetime`

#### HabitProgress extends HabitBase
- `id: int`
- `times_did: int | null` (legacy; equals number of events today)

#### HabitStatistics
- `habit_id: int`, `name: string`
- `percent_complete: int`
- `today_done: int`, `times_per_day: int`, `current_streak: int`
- `week_done: int`, `week_expected: int`
- `month_done: int`, `month_expected: int`

#### CommonProgress
- `habit_count: int`, `percent_complete: int`
- `total_completed: int`, `total_expected: int`
- `today_done: int`, `today_expected: int`
- `week_done: int`, `week_expected: int`
- `month_done: int`, `month_expected: int`

#### NotificationBase
- `time_in_seconds: int | null` (0..86399; null means unscheduled)

#### NotificationCreate extends NotificationBase
- `habit_id: int`

#### Notification extends NotificationBase
- `id: int`
- `habit_id: int`

#### TodayNotification
- `habit_id: int`
- `notification_id: int | null` (null for placeholder when habit has no notifications)
- `time_in_seconds: int | null`

#### HabitEventBase
- `timestamp: datetime | null` (if null, DB may default to now)

#### HabitEvent extends HabitEventBase
- `id: int`
- `notification_id: int`
- `timestamp: datetime`

---

### Habits API

#### POST `/v1/habits`
Create a habit.
- Body: `HabitCreate`
- Response: `Habit`

Example:
```json
{
  "user_id": 1,
  "name": "Read",
  "start_date": "2025-04-07",
  "times_per_day": 1,
  "repeat_type": "daily",
  "days_mask": 1
}
```

#### GET `/v1/habits`
List all habits for a user.
- Query: `user_id: int`
- Response: `Habit[]`

#### GET `/v1/habits/all-active`
List habits active on a given date (within date range and matching repeat/day mask).
- Query: `user_id: int`, `today: date`
- Response: `Habit[]`

#### GET `/v1/habits/habit`
Get a habit by name.
- Query: `user_id: int`, `habit_name: string`
- Response: `Habit` (404 if not found)

#### GET `/v1/habits/{habit_id}`
Get a habit by id (ownership enforced).
- Query: `user_id: int`
- Response: `Habit` (404 if not found)

#### PATCH `/v1/habits`
Update a habit.
- Body: `HabitUpdate`
- Response: `Habit`

#### DELETE `/v1/habits/{habit_id}`
Delete a habit.
- Query: `user_id: int`
- Response: `null`

#### GET `/v1/habits/{habit_id}/event`
Get habit’s events for a specific date.
- Query: `target_date: date`
- Response: `HabitEvent[]`

#### GET `/v1/habits/event/progress`
Progress for all habits on a date.
- Query: `user_id: int`, `habit_date: date`, `unfinished_only: bool=false`
- Response: `HabitProgress[]`
- Semantics: A habit is “finished” when all scheduled notifications for that date have events. When `unfinished_only=true`, returns habits that have at least one scheduled notification but fewer events than scheduled.

#### GET `/v1/habits/event/statistics`
Statistics for a specific habit up to `today`.
- Query: `user_id: int`, `habit_id: int`, `today: date`
- Response: `HabitStatistics`

#### GET `/v1/habits/event/statistics/all`
Aggregate statistics for all user habits up to `today`.
- Query: `user_id: int`, `today: date`
- Response: `CommonProgress`

---

### Notifications API

#### POST `/v1/notifications`
Create a notification for a habit.
- Body: `NotificationCreate`
- Response: `Notification`

Examples:
```json
{ "habit_id": 42 }
```
```json
{ "habit_id": 42, "time_in_seconds": 37800 }
```

#### GET `/v1/notifications/habit/{habit_id}/today`
Get today’s concrete notification times for a habit (only if the habit is active today).
- Query: `user_id: int`, `habit_id: int` (duplicate of path id), `today: date`
- Response: `string[]` as times (FastAPI serializes `time` list; derived from `time_in_seconds`)

#### GET `/v1/notifications/all`
Get habits that have at least one notification in the window `[now, now + period]` (seconds).
- Query: `now: datetime`, `period: int`
- Response: `Habit[]`
- Notes: Window can cross midnight; weekly/monthly masks are respected for `now.date()`.

#### GET `/v1/notifications/today`
Get all today’s notifications across user habits. Habits without notifications appear as placeholders.
- Query: `user_id: int`, `today: date`
- Response: `TodayNotification[]`

Example response (mixed):
```json
[
  { "habit_id": 1, "notification_id": 10, "time_in_seconds": 36000 },
  { "habit_id": 2, "notification_id": null, "time_in_seconds": null }
]
```

#### POST `/v1/notifications/{notification_id}/event`
Create a completion event for a specific notification. Duplicate same-day events for the same notification are rejected per user timezone.
- Body: `HabitEventBase` (e.g., `{ "timestamp": "2025-04-07T10:00:00Z" }`)
- Response: `HabitEvent`
- Errors:
  - 404 if `notification_id` not found
  - 422 if an event for this notification already exists between the user’s start/end of today

---

### Key Behaviors and Notes
- Day masks and repeat_type determine which days a habit is active. A habit without notifications still appears in `/v1/notifications/today` as a placeholder item.
- Completion (finished) for a day means: number of events for the habit’s scheduled notifications equals the number of scheduled notifications that day.
- `time_in_seconds` is the number of seconds after midnight. Convert from/to `HH:MM:SS` as needed.
- Timezone: duplicate-prevention for events uses the user’s timezone when checking “today” boundaries.

---

### Minimal Flows
- Create habit -> add 0..N notifications -> on due time, POST event to `/v1/notifications/{notification_id}/event`.
- Get all due notifications for today: `/v1/notifications/today?user_id=...&today=YYYY-MM-DD`.
- Daily progress list (unfinished only): `/v1/habits/event/progress?user_id=...&habit_date=...&unfinished_only=true`.
