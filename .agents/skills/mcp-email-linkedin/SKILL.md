---
name: mcp-email-linkedin
description: >-
  Provides guide and reference for using the Gmail and LinkedIn Model Context Protocol (MCP) servers
  in the Personal AI Manager project. Use when interacting with email messages, triaging incoming recruiter
  communications, generating drafts, or managing LinkedIn connection requests and posts.
---

# Gmail & LinkedIn MCP Integration Guide

This workspace is integrated with two Model Context Protocol (MCP) servers:

## 1. Gmail MCP Server (`gmail`)
- **Tools**:
  - `list_unread_emails`: Scans inbox for unread recruiter/application messages.
  - `read_email`: Reads full headers, body, and metadata.
  - `draft_email_reply`: Creates safe drafts without sending.
  - `send_email`: Transmits emails externally (strictly requires `approved=True` via Human-In-The-Loop gate).
  - `get_mailbox_status`: Reports connection health, email address, and authentication state.

## 2. LinkedIn Browser Automation MCP Server (`linkedin`)
- **Tools**:
  - `get_linkedin_profile`: Inspects candidate or target user profiles.
  - `list_connection_requests`: Checks pending inbound invitations and notes.
  - `list_recent_messages`: Checks recent recruiter conversations.
  - `send_connection_invite`: Sends connection requests (strictly under 300 characters, requires approval).
  - `publish_post`: Publishes approved post updates to feed.
  - `like_post`: Reacts with Like to a LinkedIn post (requires approval).
  - `comment_on_post`: Publishes comments on a target LinkedIn post (requires approval).
  - `get_linkedin_status`: Checks session cookie (`li_at`) status and Playwright configuration.

## Safety & Human-In-The-Loop Guardrails
External transmissions (`send_email`, `publish_post`, `send_connection_invite`, `like_post`, `comment_on_post`) are gated by the Personal AI Manager security model. The agent will always stage draft actions and request approval before calling live sending tools.
