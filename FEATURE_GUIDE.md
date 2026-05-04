# MeTube Feature Guide (Branch Additions)

This document explains every major feature added on this branch, including:
- what the feature is,
- the request/response flow,
- how to use it.

---

## 1) Upload Processing + Transcode Status + Thumbnail Placeholder

### What it is
When a user uploads a video, the app now runs a lightweight post-upload processing function that:
- marks transcoding state,
- generates a fallback thumbnail path if one was not uploaded.

### Flow
1. Authenticated user submits `POST /videos/upload` with video data.
2. `videos.views.upload_video` saves the `Video` row.
3. `utils.process_uploaded_video(video)` runs:
   - sets `transcode_status='processing'`,
   - then `transcode_status='completed'`,
   - assigns `thumbnail_file` fallback (`thumbnails/generated/<filename>.jpg`) when missing,
   - on exception sets `transcode_status='failed'`.
4. User is redirected to home page.

### How to use
- Log in.
- Open **Upload** in navbar.
- Upload a video.
- Open watch page to see transcode status and video details.

---

## 2) Subscriptions (Follow/Unfollow Creators)

### What it is
Users can subscribe to creators and unsubscribe later.

### Data model
- `users.Subscription`
  - `subscriber` (user)
  - `creator` (user)
  - unique constraint on `(subscriber, creator)`

### Flow
1. Authenticated viewer opens a watch page owned by another user.
2. Viewer clicks **Subscribe/Unsubscribe**.
3. Frontend sends `POST /accounts/subscribe/<creator_id>/`.
4. `users.views.toggle_subscription`:
   - creates row if missing -> `{subscribed: true}`
   - deletes row if existing -> `{subscribed: false}`
   - rejects self-subscribe with HTTP 400.

### How to use
- Log in.
- Open any other creator's watch page.
- Click **Subscribe**.
- Click again to unsubscribe.

---

## 3) Recommendations Pipeline

### What it is
A recommendation engine generates a `recommended_vids` list for homepage.

### Flow
`streamingservice.recommendations.get_recommendations_for_user(user, limit=10)`
1. Builds candidate set of public, completed videos.
2. For authenticated users with subscriptions:
   - prioritizes videos from subscribed creators,
   - backfills with popular videos.
3. For users without subscriptions:
   - uses trending-this-week fallback,
   - then recent uploads fallback.
4. Returns `RecommendationItem(video, score, reason)` entries.

### How to use
- Visit `/`.
- See **Recommended for you** list with reason labels.

---

## 4) Homepage Search + Sort

### What it is
Homepage now supports filtering and ordering the main video list.

### Flow
1. User submits GET params on `/`:
   - `q` (search text)
   - `sort=latest|popular`
2. `IndexView.get_queryset`:
   - filters by `title` or `description` (`icontains`) when `q` exists,
   - sorts by newest or popularity fields.

### How to use
- On `/`, type in search box.
- Pick **Latest** or **Popular**.
- Click **Apply**.

---

## 5) Subscription Feed on Homepage

### What it is
Authenticated users see a section showing recent uploads from creators they follow.

### Flow
1. `IndexView.get_context_data` checks subscriptions for current user.
2. Pulls latest public videos from those creator IDs.
3. Exposes `subscription_vids` to template.

### How to use
- Subscribe to one or more creators.
- Go to `/`.
- See **From your subscriptions** block.

---

## 6) Watch Page View Tracking (Per Session)

### What it is
Opening a watch page increments video views only once per session per video.

### Flow
1. User requests `GET /videos/watch/<id>`.
2. View checks session key `viewed_video_<id>`.
3. If missing:
   - increments `Video.views`,
   - stores session key.
4. Future requests in same session do not increment again.

### How to use
- Open a video once (view count increments).
- Refresh in same browser session (count stays stable).

---

## 7) Comments

### What it is
Authenticated users can add comments to videos; watch page renders comment list.

### Flow
1. User submits comment form on watch page.
2. Frontend sends `POST /comments/add/<video_id>/`.
3. `comments.views.add_comment` creates `Comment` and redirects back.
4. `videos.views.watch_video` loads comments ordered by latest.
5. `Comment.save()` updates `video.num_comments`.

### How to use
- Log in.
- Open watch page.
- Enter text in comment box and submit.
- Comment appears in list.

---

## 8) Related Videos (Same Creator)

### What it is
Watch page shows other public uploads from the same creator.

### Flow
1. `watch_video` queries public videos by `uploaded_by`, excluding current video.
2. Sends top 5 most recent as `related_videos` to template.
3. Template renders under **More from <creator>**.

### How to use
- Open any watch page.
- Scroll to **More from ...** section.
- Click another video from same creator.

---

## 9) Routing/Template Integration Fixes Included on Branch

### What changed
- Added comments URL include in project router.
- Added `users` URL namespace and profile route for navbar links.
- Updated base template to load `django_bootstrap5` tags.
- Guarded video poster tag so missing thumbnails do not crash rendering.

### How to validate quickly
- Visit `/` and `/videos/watch/<id>` while logged in/out.
- Verify navbar links resolve.
- Verify watch page renders even when no thumbnail is present.

---

## 10) Test Coverage Added on This Branch

Automated tests were added for:
- subscription toggling,
- recommendations behavior,
- upload processing,
- watch view-count behavior,
- comment creation,
- index search/sort and subscription feed rendering.

Run:
```bash
python manage.py test --settings=streamingservice.test_settings
```
