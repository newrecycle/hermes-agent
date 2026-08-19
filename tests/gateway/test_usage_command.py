@@ -245,6 +245,33 @@ async def _fake_to_thread(fn, *args, **kwargs):
         assert "📈 **Account limits**" in result
 
 
+class TestCodexUsageCommand:
+    @pytest.mark.asyncio
+    async def test_codex_usage_command_returns_markdown_usage(self, monkeypatch):
+        runner = _make_runner(SK)
+        event = MagicMock()
+        snapshot = MagicMock(available=True)
+
+        monkeypatch.setattr(
+            "gateway.slash_commands.fetch_account_usage",
+            lambda provider, base_url=None, api_key=None: snapshot if provider == "openai-codex" else None,
+        )
+        monkeypatch.setattr(
+            "gateway.slash_commands.render_account_usage_lines",
+            lambda snap, markdown=False: [
+                "📈 **Account limits**",
+                "Provider: openai-codex (Pro)",
+                "Session: 85% remaining (15% used) • resets in 2h",
+            ],
+        )
+
+        result = await runner._handle_codex_usage_command(event)
+
+        assert "openai-codex (Pro)" in result
+        assert "85% remaining" in result
+        assert "resets in 2h" in result
+
+
 class TestUsageContextBreakdown:
     """The /usage output includes the per-category context breakdown."""
