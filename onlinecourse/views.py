from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Course, Enrollment, Submission, Choice

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        enrollment = Enrollment.objects.filter(course=course).first() 
        if not enrollment:
            return redirect('onlinecourse:course_details', course_id=course.id)
            
        submission = Submission.objects.create(enrollment=enrollment)
        
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                choice_id = value
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
                
        submission.save()
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_questions = course.question_set.count()
    correct_answers = 0
    
    for question in course.question_set.all():
        selected_choices = submission.choices.filter(question=question)
        correct_choices = question.choice_set.filter(is_correct=True)
        
        if set(selected_choices) == set(correct_choices):
            correct_answers += 1
            
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= 80
    
    context = {
        'course': course,
        'score': score,
        'passed': passed,
        'submission': submission,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
