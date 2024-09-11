from django.shortcuts import render, get_object_or_404, redirect
from django.core.handlers.wsgi import WSGIRequest
from item.models import Item
from .models import Conversation, ConversationMessage
from .forms import ConversationMessageForm
from django.contrib.auth.decorators import login_required

@login_required
def new_conversation(request: WSGIRequest, item_pk):
    item = get_object_or_404(Item, pk=item_pk)
    
    if item.created_by == request.user:
        return redirect('dashboard:index')
    
    conversations = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])
    
    if conversations:
        return redirect('conversation:detail', pk=conversations.first().id)
    
    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)
        if form.is_valid():
            conversation = Conversation.objects.create(item=item)
            conversation.members.add(request.user)
            conversation.members.add(item.created_by)
            conversation.save()
            
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()
            return redirect('item:detail', pk=item_pk)
    else:
        form = ConversationMessageForm
    
    context = {
        'form': form
    }
    return render(request, 'conversation/new.html', context)

@login_required
def inbox(request: WSGIRequest):
    conversations = Conversation.objects.filter(members__in=[request.user.id])
    context = {
        'conversations': conversations
    }
    return render(request, 'conversation/inbox.html', context)
    
@login_required
def detail(request: WSGIRequest, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
            
    if request.method == "POST":
        form = ConversationMessageForm(request.POST)
        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()
            
            conversation.save()
            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()
    
    context = {
        'conversation': conversation,
        'form': form
    }
    
    for member in conversation.members.all():
        if member != request.user:
            context['recepient'] = member
    
    return render(request, 'conversation/detail.html', context)
    