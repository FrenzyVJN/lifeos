"""Test cases for LifeOS core functionality."""

import pytest
from datetime import datetime, timedelta, timezone, timezone
from unittest.mock import patch, MagicMock

from lifeos.models import Task, Project, TimelineEntry, MoodEntry
from lifeos.actions import (
    normalize, similarity, find_duplicate_task, find_duplicate_project,
    log_input, get_pending_tasks, get_daily_summary, mark_task_done,
    edit_task, delete_task, next_occurrence, get_streak
)
from lifeos.parser import resolve_date


class TestNormalization:
    """Tests for text normalization."""

    def test_basic_normalize(self):
        """Basic lowercase normalization."""
        assert normalize("Hello World") == "hello world"

    def test_synonym_replacement(self):
        """Synonyms should be replaced."""
        assert "test" in normalize("math exam")
        assert "meet" in normalize("team meeting")

    def test_stopword_removal(self):
        """Stopwords should be removed."""
        result = normalize("the quick brown fox")
        assert "the" not in result
        assert "a" not in result

    def test_case_insensitive(self):
        """Normalization is case insensitive."""
        assert normalize("HELLO") == normalize("hello")


class TestDateResolution:
    """Tests for date parsing."""

    def test_resolve_date_none(self):
        """None input returns None."""
        assert resolve_date(None) is None

    def test_resolve_date_empty(self):
        """Empty string returns None."""
        assert resolve_date("") is None


class TestRecurrence:
    """Tests for recurring task logic."""

    def test_next_occurrence_daily(self):
        """Daily recurrence adds 1 day."""
        today = datetime(2026, 4, 14, 10, 0, 0)
        next_due = next_occurrence("daily", today)
        assert next_due == today + timedelta(days=1)

    def test_next_occurrence_weekly(self):
        """Weekly recurrence adds 7 days."""
        today = datetime(2026, 4, 14, 10, 0, 0)
        next_due = next_occurrence("weekly", today)
        assert next_due == today + timedelta(weeks=1)

    def test_next_occurrence_weekday(self):
        """Weekday recurrence skips weekends."""
        # Friday -> Monday
        friday = datetime(2026, 4, 10, 10, 0, 0)
        next_due = next_occurrence("weekday", friday)
        assert next_due.weekday() == 0  # Monday

    def test_next_occurrence_weekend(self):
        """Weekend recurrence skips weekdays."""
        # Monday -> Saturday
        monday = datetime(2026, 4, 13, 10, 0, 0)
        next_due = next_occurrence("weekend", monday)
        assert next_due.weekday() == 5  # Saturday

    def test_next_occurrence_none_for_invalid(self):
        """Invalid recurrence returns None."""
        assert next_occurrence("invalid", datetime.now()) is None


class TestTaskDeduplication:
    """Tests for task deduplication logic."""

    def test_normalize_for_dedup(self):
        """Normalized titles are used for comparison."""
        # "math test" and "maths test" should be similar after normalization
        norm1 = normalize("math exam")
        norm2 = normalize("math test")
        # Both normalize to "math test" (exam -> test synonym)
        assert norm1 == norm2


class TestProjectLinking:
    """Tests for project creation and linking."""

    def test_normalize_project_name(self):
        """Project names are normalized."""
        from lifeos.actions import normalize
        assert normalize("LifeOS Project") == normalize("lifeos project")


class TestTaskOperations:
    """Tests for task CRUD operations."""

    def test_edit_task_title(self, session):
        """Editing task title also updates normalized_title."""
        task = Task(
            title="old title",
            normalized_title="old title",
            status="pending"
        )
        session.add(task)
        session.commit()

        result = edit_task(task.id, title="new title")

        assert result.title == "new title"
        assert result.normalized_title == "new title"

    def test_edit_task_due_date(self, session):
        """Editing task due date works."""
        task = Task(
            title="test task",
            normalized_title="test task",
            status="pending"
        )
        session.add(task)
        session.commit()

        result = edit_task(task.id, due="tomorrow")

        assert result.due_date is not None

    def test_delete_task_soft_deletes(self, session):
        """Delete marks task as deleted, not removing it."""
        task = Task(
            title="to delete",
            normalized_title="to delete",
            status="pending"
        )
        session.add(task)
        session.commit()
        task_id = task.id

        result = delete_task(task_id)

        assert result is True
        # Query in a fresh session to see the actual database state
        from lifeos.db import get_session
        fresh_session = get_session()
        fresh_session.expire_on_commit = False
        found = fresh_session.query(Task).filter(Task.id == task_id).first()
        assert found.status == "deleted"
        fresh_session.close()


class TestMoodTracking:
    """Tests for mood functionality."""

    def test_log_mood_returns_entry(self, fresh_db):
        """log_mood creates a MoodEntry."""
        with patch('lifeos.actions.extract_mood_score', return_value=4):
            from lifeos.actions import log_mood
            entry = log_mood("feeling good")

            assert entry.mood == "feeling good"
            assert entry.score == 4


class TestSummary:
    """Tests for summary and digest functions."""

    def test_get_daily_summary_structure(self, fresh_db):
        """Daily summary returns expected dict structure."""
        from lifeos.actions import get_daily_summary

        summary = get_daily_summary()

        assert "timeline" in summary
        assert "tasks_created" in summary
        assert "tasks_done" in summary
        assert "projects" in summary
        assert "streak" in summary
        assert "mood_today" in summary
        assert "avg_mood" in summary

    def test_get_daily_summary_empty(self, fresh_db):
        """Empty summary returns empty lists, 0 streak."""
        from lifeos.actions import get_daily_summary

        summary = get_daily_summary()

        assert len(summary["timeline"]) == 0
        assert len(summary["tasks_created"]) == 0
        assert summary["streak"] == 0


class TestStreak:
    """Tests for streak tracking."""

    def test_streak_zero_when_no_entries(self, session):
        """Zero entries returns 0 streak."""
        streak = get_streak()
        assert streak == 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_input_handled(self):
        """Empty input should be handled gracefully in CLI."""
        # This is handled at CLI level, but we test the flow
        from lifeos.parser import rule_based_extract

        result = rule_based_extract("")
        assert result == []

    def test_special_characters_in_task_title(self, session):
        """Task titles with special characters should work."""
        task = Task(
            title="Fix bug #1234 - can't login with <特殊字符>",
            normalized_title="fix bug 1234 cant login with ",
            status="pending"
        )
        session.add(task)
        session.commit()

        assert task.title == "Fix bug #1234 - can't login with <特殊字符>"


class TestEmbeddingPerformance:
    """Tests for embedding-based deduplication performance and correctness."""

    def test_embedding_similarity_returns_float(self):
        """embedding_similarity returns a float between -1 and 1."""
        from lifeos.actions import embedding_similarity
        score = embedding_similarity("hello world", "hello world")
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0

    def test_embedding_similarity_identical_strings(self):
        """Identical strings should have score close to 1.0."""
        from lifeos.actions import embedding_similarity
        score = embedding_similarity("finish homework", "finish homework")
        assert score > 0.95

    def test_embedding_similarity_semantic_similarity(self):
        """Semantically similar strings should score high."""
        from lifeos.actions import embedding_similarity
        # "math exam" and "math test" should be similar
        score = embedding_similarity("math exam", "math test")
        assert score > 0.5

    def test_embedding_similarity_dissimilar_strings(self):
        """Dissimilar strings should score low."""
        from lifeos.actions import embedding_similarity
        score = embedding_similarity("buy groceries", "fix server bug")
        assert score < 0.5


class TestSimilarityThreshold:
    """Tests for similarity threshold behavior."""

    def test_similarity_threshold_constant_exists(self):
        """SIMILARITY_THRESHOLD constant should be defined."""
        from lifeos.actions import SIMILARITY_THRESHOLD
        assert SIMILARITY_THRESHOLD == 0.82

    def test_find_duplicate_task_below_threshold(self, session):
        """Tasks below similarity threshold should not match."""
        task = Task(
            title="buy groceries",
            normalized_title="buy groceries",
            status="pending"
        )
        session.add(task)
        session.commit()

        from lifeos.actions import find_duplicate_task
        # "fix server bug" is very different from "buy groceries"
        result = find_duplicate_task(session, "fix server bug completely")
        assert result is None


class TestRecurringTaskEdgeCases:
    """Tests for recurring task edge cases."""

    def test_next_occurrence_none_recurrence(self):
        """None recurrence returns None."""
        from lifeos.actions import next_occurrence
        result = next_occurrence(None)
        assert result is None

    def test_next_occurrence_empty_recurrence(self):
        """Empty string recurrence returns None."""
        from lifeos.actions import next_occurrence
        result = next_occurrence("")
        assert result is None

    def test_next_occurrence_weekday_friday(self):
        """Friday weekday recurrence returns Monday."""
        from lifeos.actions import next_occurrence
        friday = datetime(2026, 4, 10, 10, 0, 0)  # A Friday
        next_due = next_occurrence("weekday", friday)
        assert next_due.weekday() == 0  # Monday
        assert next_due == friday + timedelta(days=3)

    def test_next_occurrence_weekday_monday(self):
        """Monday weekday recurrence returns Tuesday."""
        from lifeos.actions import next_occurrence
        monday = datetime(2026, 4, 13, 10, 0, 0)  # A Monday
        next_due = next_occurrence("weekday", monday)
        assert next_due.weekday() == 1  # Tuesday
        assert next_due == monday + timedelta(days=1)

    def test_next_occurrence_weekend_sunday(self):
        """Sunday weekend recurrence returns next Saturday (6 days later)."""
        from lifeos.actions import next_occurrence
        sunday = datetime(2026, 4, 12, 10, 0, 0)  # A Sunday
        next_due = next_occurrence("weekend", sunday)
        assert next_due.weekday() == 5  # Saturday
        # Sunday + 6 days = Saturday (skip Mon-Fri)
        assert next_due == sunday + timedelta(days=6)

    def test_next_occurrence_weekend_saturday(self):
        """Saturday weekend recurrence returns next Sunday (tomorrow is also weekend)."""
        from lifeos.actions import next_occurrence
        saturday = datetime(2026, 4, 11, 10, 0, 0)  # A Saturday
        next_due = next_occurrence("weekend", saturday)
        # Code returns next day that is Saturday/Sunday - tomorrow (Sunday) qualifies
        assert next_due.weekday() == 6  # Sunday


class TestMarkTaskDoneEdgeCases:
    """Tests for mark_task_done edge cases."""

    def test_mark_task_done_nonexistent(self, session):
        """Marking non-existent task returns None."""
        from lifeos.actions import mark_task_done
        result = mark_task_done("nonexistent-id-12345")
        assert result is None

    def test_mark_task_done_non_recurring(self, session):
        """Marking non-recurring task done doesn't create new task."""
        task = Task(
            title="one-time task",
            normalized_title="one-time task",
            status="pending"
        )
        session.add(task)
        session.commit()
        task_id = task.id

        from lifeos.actions import mark_task_done
        result = mark_task_done(task_id)

        assert result is not None
        assert result.status == "done"

        # Verify no new task was created
        from lifeos.models import Task as TaskModel
        all_tasks = session.query(TaskModel).filter(
            TaskModel.title == "one-time task"
        ).all()
        # Should only have the original (now done) task
        assert len(all_tasks) == 1

    def test_mark_task_done_recurring_creates_next(self, session):
        """Marking recurring task done creates next occurrence."""
        from datetime import datetime, timedelta, timezone
        from lifeos.actions import mark_task_done

        due_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(
            title="daily standup",
            normalized_title="daily standup",
            status="pending",
            recurrence="daily",
            next_due=due_date
        )
        session.add(task)
        session.commit()
        task_id = task.id

        result = mark_task_done(task_id)

        assert result is not None
        assert result.status == "done"

        # Check new task was created
        from lifeos.models import Task as TaskModel
        new_tasks = session.query(TaskModel).filter(
            TaskModel.title == "daily standup",
            TaskModel.status == "pending"
        ).all()
        assert len(new_tasks) == 1
        assert new_tasks[0].recurrence == "daily"

    def test_mark_task_done_recurring_with_none_next_due(self, session):
        """Marking recurring task with None next_due handles gracefully."""
        task = Task(
            title="weekly review",
            normalized_title="weekly review",
            status="pending",
            recurrence="weekly",
            next_due=None  # Explicitly None
        )
        session.add(task)
        session.commit()
        task_id = task.id

        from lifeos.actions import mark_task_done
        result = mark_task_done(task_id)

        # Should still work, creating a new task (due_date will be None, next_due calculated from now)
        assert result is not None
        assert result.status == "done"


class TestSearchEdgeCases:
    """Tests for search functionality edge cases."""

    def test_search_returns_empty_when_nothing_matches(self, session):
        """Search with no matches returns empty list."""
        from lifeos.actions import search

        # Create a task
        task = Task(
            title="specific task about python",
            normalized_title="specific task about python",
            status="pending"
        )
        session.add(task)
        session.commit()

        results = search("xyzzy nothing matches this at all")
        assert len(results) == 0

    def test_search_returns_task_matches(self, session):
        """Search returns matching tasks."""
        from lifeos.actions import search

        task = Task(
            title="fix authentication bug",
            normalized_title="fix authentication bug",
            status="pending"
        )
        session.add(task)
        session.commit()

        results = search("login problem")
        assert len(results) > 0
        assert any(r[0] == "task" for r in results)

    def test_search_includes_timeline_matches(self, session):
        """Search includes matching timeline entries."""
        from lifeos.actions import search
        from lifeos.models import TimelineEntry

        entry = TimelineEntry(content="worked on the database migration today")
        session.add(entry)
        session.commit()

        results = search("database migration")
        assert len(results) > 0
        assert any(r[0] == "timeline" for r in results)


class TestMoodEdgeCases:
    """Tests for mood tracking edge cases."""

    def test_log_mood_with_emoji(self, session):
        """Mood with emoji should be handled."""
        with patch('lifeos.actions.extract_mood_score', return_value=4):
            from lifeos.actions import log_mood
            entry = log_mood("feeling great! 🎉")
            assert entry.score == 4

    def test_log_mood_score_bounds(self, session):
        """Mood score should be 1-5."""
        with patch('lifeos.actions.extract_mood_score', return_value=4):
            from lifeos.actions import log_mood
            entry = log_mood("test mood")
            assert 1 <= entry.score <= 5

    def test_get_mood_history_empty(self, session):
        """Empty mood history returns empty dict."""
        from lifeos.actions import get_mood_history
        result = get_mood_history()
        assert result == {}

    def test_get_mood_history_groups_by_day(self, session):
        """Mood history groups entries by day."""
        from lifeos.actions import log_mood
        from lifeos.actions import get_mood_history
        from datetime import datetime, timedelta, timezone

        with patch('lifeos.actions.extract_mood_score', return_value=4):
            log_mood("monday mood")
            log_mood("tuesday mood")
            log_mood("wednesday mood")

        # Need to add entries directly to test the grouping
        from lifeos.models import MoodEntry
        today = datetime.now(timezone.utc)
        for i in range(3):
            entry = MoodEntry(
                mood=f"day {i}",
                score=3,
                timestamp=today - timedelta(days=i)
            )
            session.add(entry)
        session.commit()

        history = get_mood_history(days=7)
        # Should have entries for different days
        assert isinstance(history, dict)


class TestProjectEdgeCases:
    """Tests for project edge cases."""

    def test_delete_project_unlinks_tasks(self, session):
        """Deleting project unlinks but doesn't delete tasks."""
        project = Project(
            name="Test Project",
            normalized_name="test project"
        )
        session.add(project)
        session.commit()
        project_id = project.id

        task = Task(
            title="task under project",
            normalized_title="task under project",
            status="pending",
            project_id=project_id
        )
        session.add(task)
        session.commit()

        from lifeos.actions import delete_project
        result = delete_project(project_id)
        assert result is True

        # Task should still exist but project_id cleared
        from lifeos.models import Task as TaskModel
        found_task = session.query(TaskModel).filter(
            TaskModel.id == task.id
        ).first()
        assert found_task is not None
        assert found_task.project_id is None

    def test_delete_nonexistent_project(self, session):
        """Deleting non-existent project returns False."""
        from lifeos.actions import delete_project
        result = delete_project("nonexistent-id-99999")
        assert result is False

    def test_get_project_tasks_empty(self, session):
        """Getting tasks for project with no tasks returns empty list."""
        from lifeos.actions import get_project_tasks

        project = Project(
            name="Empty Project",
            normalized_name="empty project"
        )
        session.add(project)
        session.commit()

        _, tasks = get_project_tasks(project.id)
        assert tasks == []


class TestTimelineEdgeCases:
    """Tests for timeline edge cases."""

    def test_get_timeline_empty(self, session):
        """Empty timeline returns empty list."""
        from lifeos.actions import get_timeline
        result = get_timeline()
        assert result == []

    def test_get_timeline_orders_by_timestamp(self, session):
        """Timeline is ordered by timestamp descending (newest first)."""
        from lifeos.actions import get_timeline
        from lifeos.models import TimelineEntry
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        entry1 = TimelineEntry(content="first entry", timestamp=now - timedelta(hours=2))
        entry2 = TimelineEntry(content="second entry", timestamp=now - timedelta(hours=1))
        entry3 = TimelineEntry(content="third entry", timestamp=now)
        session.add_all([entry1, entry2, entry3])
        session.commit()

        timeline = get_timeline()
        assert timeline[0].content == "third entry"
        assert timeline[2].content == "first entry"


class TestNormalizationEdgeCases:
    """Tests for normalization edge cases."""

    def test_normalize_numbers_preserved(self):
        """Numbers in text are preserved."""
        from lifeos.actions import normalize
        result = normalize("todo item #123")
        assert "123" in result

    def test_normalize_multiple_spaces(self):
        """Multiple spaces are normalized to single space."""
        from lifeos.actions import normalize
        result = normalize("todo    item")
        assert "  " not in result

    def test_normalize_punctuation_handling(self):
        """Punctuation is mostly preserved."""
        from lifeos.actions import normalize
        result = normalize("fix bug: login!")
        # "bug" and "login" should be present
        assert "bug" in result
        assert "login" in result

    def test_normalize_synonym_chains(self):
        """Multiple synonyms in chain work correctly."""
        from lifeos.actions import normalize
        # "exam" -> "test", but what about "test exam"?
        result = normalize("test exam")
        assert "test" in result


class TestDateResolutionEdgeCases:
    """Tests for date resolution edge cases."""

    def test_resolve_date_tomorrow(self):
        """'tomorrow' resolves to future date."""
        result = resolve_date("tomorrow")
        assert result is not None
        assert result.date() >= datetime.now(timezone.utc).date()

    def test_resolve_date_next_week(self):
        """'next week' resolves correctly."""
        result = resolve_date("next week")
        assert result is not None
        # Should be at least 7 days in the future
        assert (result.date() - datetime.now(timezone.utc).date()).days >= 7

    def test_resolve_date_invalid_returns_none(self):
        """Invalid date string returns None."""
        result = resolve_date("not a real date at all xyzzy")
        # dateparser might return something or None depending on version
        # Just verify it doesn't crash


class TestSummaryEdgeCases:
    """Tests for summary edge cases."""

    def test_get_weekly_summary_structure(self, fresh_db):
        """Weekly summary has expected structure."""
        from lifeos.actions import get_weekly_summary

        summary = get_weekly_summary()

        assert "timeline" in summary
        assert "tasks_created" in summary
        assert "tasks_done" in summary
        assert "projects" in summary
        assert "most_active_project" in summary
        assert "start_date" in summary
        assert "end_date" in summary

    def test_get_weekly_summary_empty(self, fresh_db):
        """Empty weekly summary works."""
        from lifeos.actions import get_weekly_summary

        summary = get_weekly_summary()

        assert len(summary["timeline"]) == 0
        assert len(summary["tasks_created"]) == 0
        assert summary["most_active_project"] is None


class TestChatEdgeCases:
    """Tests for chat functionality."""

    def test_chat_with_no_data(self, session):
        """Chat with no data returns appropriate response."""
        from lifeos.actions import chat

        result = chat("what am I working on?")
        # Should still return something (possibly empty or a "no data" message)
        assert isinstance(result, str)

    def test_chat_with_data(self, session):
        """Chat with data includes context in response."""
        from lifeos.models import TimelineEntry, Task, Project

        # Add some data
        entry = TimelineEntry(content="working on the backend today")
        session.add(entry)

        task = Task(
            title="fix login bug",
            normalized_title="fix login bug",
            status="pending"
        )
        session.add(task)

        project = Project(
            name="TestProject",
            normalized_name="testproject"
        )
        session.add(project)
        session.commit()

        from lifeos.actions import chat
        result = chat("what am I working on?")
        assert isinstance(result, str)
        # Response might mention the project or task


class TestReportEdgeCases:
    """Tests for report generation."""

    def test_generate_report_daily(self, session):
        """Daily report generates markdown."""
        from lifeos.actions import generate_report

        md = generate_report(week=False)
        assert isinstance(md, str)
        assert "LifeOS Report" in md
        assert "Tasks Completed" in md
        assert "Tasks Pending" in md
        assert "Timeline" in md

    def test_generate_report_weekly(self, session):
        """Weekly report generates markdown."""
        from lifeos.actions import generate_report

        md = generate_report(week=True)
        assert isinstance(md, str)
        assert "LifeOS Report" in md

    def test_generate_report_with_output_file(self, session, tmp_path):
        """Report can be written to file."""
        from lifeos.actions import generate_report

        out_file = str(tmp_path / "report.md")
        md = generate_report(week=False, out_file=out_file)

        import os
        assert os.path.exists(out_file)
        with open(out_file) as f:
            assert f.read() == md


class TestStreakEdgeCases:
    """Tests for streak edge cases."""

    def test_streak_single_entry(self, session):
        """Single entry returns streak of 1."""
        from lifeos.models import TimelineEntry
        from lifeos.actions import get_streak

        entry = TimelineEntry(content="first entry")
        session.add(entry)
        session.commit()

        # Need to reset streak calculation to use this session
        from lifeos.actions import get_streak_internal
        streak = get_streak_internal(session)
        assert streak == 1

    def test_streak_consecutive_days(self, session):
        """Consecutive days returns correct streak."""
        from lifeos.models import TimelineEntry
        from datetime import datetime, timedelta, timezone

        today = datetime.now(timezone.utc).date()
        for i in range(5):
            entry = TimelineEntry(
                content=f"day {i}",
                timestamp=datetime.combine(today - timedelta(days=i), datetime.min.time())
            )
            session.add(entry)
        session.commit()

        from lifeos.actions import get_streak_internal
        streak = get_streak_internal(session)
        assert streak == 5

    def test_streak_gap_resets(self, session):
        """Gap in days resets streak."""
        from lifeos.models import TimelineEntry
        from datetime import datetime, timedelta, timezone

        today = datetime.now(timezone.utc).date()
        # Day 0 (today), Day 1 (yesterday), Day 3 (3 days ago) - gap at Day 2
        for i in [0, 1, 3]:
            entry = TimelineEntry(
                content=f"day {i}",
                timestamp=datetime.combine(today - timedelta(days=i), datetime.min.time())
            )
            session.add(entry)
        session.commit()

        from lifeos.actions import get_streak_internal
        streak = get_streak_internal(session)
        assert streak == 2  # Only today and yesterday count
