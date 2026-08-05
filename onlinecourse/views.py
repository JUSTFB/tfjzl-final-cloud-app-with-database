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
    
    selected_ids = [choice.id for choice in submission.choices.all()]
    total_score = 0
    possible_score = 0
    
    for question in course.question_set.all():
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    grade = (total_score / possible_score) * 100 if possible_score > 0 else 0
    
    context = {
        'course': course,
        'grade': grade,
        'selected_ids': selected_ids,
        'submission': submission,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
