from django.shortcuts import render
from django.utils import timezone
from .models import Post, Comment
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCy7jOWJCdYSyR20gL5FGdoGKpJCXcN-M4")

# Set up the generative model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def summarize(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Summarize the post content
    convo = model.start_chat(history=[
      {
    "role": "user",
    "parts": ["you are a blog summarizer, summarize the posts i provide without any explanation or greeting"]
  },
  {
    "role": "model",
    "parts": ["Understood. Please provide the blog posts you want me to summarize. I will condense them without any additional explanation or greeting."]
  },
  {
    "role": "user",
    "parts": ["and also dont add this in the reply **Summary:**"]
  },
  {
    "role": "model",
    "parts": ["Got it. I will simply provide the condensed summaries without any additional text like \"Summary:\". Just paste the blog posts you want me to summarize."]
  },
  {
    "role": "user",
    "parts": ["please don't provide the title also in the reply"]
  },
  {
    "role": "model",
    "parts": ["No problem. I will provide only the condensed summary, without a title or any additional text. Just paste the blog post below and I will summarize it for you."]
  },
])
    
    convo.send_message(post.text)
    summarized_text = convo.last.text
    
    return render(request, 'blog/summarized_content.html', {'post': post, 'summarized_text': summarized_text})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)\
      
      
from django.contrib.auth import logout      
  
@login_required
def logout_view(request):
    logout(request)
    return redirect('post_list')