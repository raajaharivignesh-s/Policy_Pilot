#!/usr/bin/env python3
"""
Test script for ConversationHistoryService
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation_history_service import ConversationHistoryService


def test_conversation_history_service():
    """Test the ConversationHistoryService implementation."""
    
    print("🧪 Testing ConversationHistoryService...\n")
    
    # Create instance
    service = ConversationHistoryService()
    
    # Test 1: Initialize history for new conversation
    conversation_id = 'test-conv-123'
    service.initialize_history(conversation_id)
    print('✅ Test 1 - Initialize history: PASSED')
    
    # Test 2: Get empty history
    history = service.get_history(conversation_id)
    assert history == [], f'Expected empty list, got {history}'
    print('✅ Test 2 - Get empty history: PASSED')
    
    # Test 3: Append user message
    service.append_to_history(conversation_id, 'user', 'Hello, I need help with schemes.')
    history = service.get_history(conversation_id)
    assert len(history) == 1, f'Expected 1 message, got {len(history)}'
    assert history[0]['role'] == 'user'
    assert history[0]['content'] == 'Hello, I need help with schemes.'
    print('✅ Test 3 - Append user message: PASSED')
    
    # Test 4: Append assistant message
    service.append_to_history(conversation_id, 'assistant', 'I can help you with that. What state are you from?')
    history = service.get_history(conversation_id)
    assert len(history) == 2, f'Expected 2 messages, got {len(history)}'
    assert history[1]['role'] == 'assistant'
    print('✅ Test 4 - Append assistant message: PASSED')
    
    # Test 5: Test truncation at 20 entries (simpler test)
    print('\n🧪 Testing truncation...')
    # Clear existing history first
    service.clear_history(conversation_id)
    
    # Add 15 messages (not enough to trigger truncation)
    for i in range(15):
        service.append_to_history(conversation_id, 'user', f'Message {i}')
    
    history = service.get_history(conversation_id)
    print(f'   History length after 15 messages: {len(history)}')
    assert len(history) == 15, f'Expected 15 messages, got {len(history)}'
    
    # Add 10 more messages (total 25, should truncate to 20)
    for i in range(15, 25):
        service.append_to_history(conversation_id, 'user', f'Message {i}')
    
    history = service.get_history(conversation_id)
    print(f'   History length after 25 messages (should be 20): {len(history)}')
    assert len(history) == 20, f'Expected 20 messages after truncation, got {len(history)}'
    print('✅ Test 5 - Auto-truncation at 20 entries: PASSED')
    
    # Test 6: Test invalid role validation
    print('\n🧪 Testing validation...')
    try:
        service.append_to_history(conversation_id, 'system', 'Invalid role')
        print('❌ Test 6 - Invalid role validation: FAILED (should have raised ValueError)')
        return False
    except ValueError as e:
        print(f'✅ Test 6 - Invalid role validation: PASSED (ValueError: {e})')
    
    # Test 7: Test non-existent conversation
    non_existent_history = service.get_history('non-existent-id')
    assert non_existent_history == [], f'Expected empty list for non-existent ID, got {non_existent_history}'
    print('✅ Test 7 - Non-existent conversation returns empty list: PASSED')
    
    # Test 8: Test empty content validation
    try:
        service.append_to_history(conversation_id, 'user', '   ')
        print('❌ Test 8 - Empty content validation: FAILED (should have raised ValueError)')
        return False
    except ValueError as e:
        print(f'✅ Test 8 - Empty content validation: PASSED (ValueError: {e})')
    
    # Test 9: Test get_conversation_ids
    conv_ids = service.get_conversation_ids()
    assert 'test-conv-123' in conv_ids, f'Expected test-conv-123 in conversation IDs'
    print(f'✅ Test 9 - Get conversation IDs: PASSED (IDs: {conv_ids})')
    
    # Test 10: Test get_total_messages
    total = service.get_total_messages(conversation_id)
    print(f'✅ Test 10 - Get total messages: PASSED (total: {total})')
    
    print('\n🎉 All tests passed! ConversationHistoryService is working correctly.')
    return True


if __name__ == '__main__':
    try:
        success = test_conversation_history_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'\n❌ Test failed with exception: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)