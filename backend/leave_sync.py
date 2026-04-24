from extensions import db
from datetime import date
import sys

def sync_attendance_with_leave(leave_record):
    """
    请假审批通过后，联动更新考勤记录
    
    逻辑：
    1. 查找该学生在请假时间段内、对应课程的所有上课记录
    2. 将这些上课记录中的考勤状态从'出勤'更新为'请假'
    3. 恢复被扣除的课时
    
    支持两种场景：
    - 提前请假：录入上课记录时已标记为请假（无需更新）
    - 课后补假：已将状态标记为出勤，需更新为请假并恢复课时
    """
    from models import ClassRecord, AttendanceRecord, StudentCourse
    
    print(f'[SYNC] sync_attendance_with_leave called for leave_id={leave_record.id}, student_id={leave_record.student_id}, course_id={leave_record.course_id}', flush=True)
    print(f'[SYNC] Date range: {leave_record.start_date} to {leave_record.end_date}', flush=True)
    
    student_id = leave_record.student_id
    course_id = leave_record.course_id
    start_date = leave_record.start_date
    end_date = leave_record.end_date
    
    class_records = ClassRecord.query.filter(
        ClassRecord.course_id == course_id,
        ClassRecord.class_date >= start_date,
        ClassRecord.class_date <= end_date
    ).all()
    
    print(f'[SYNC] Found {len(class_records)} class records in date range', flush=True)
    
    updated_count = 0
    hours_restored = 0
    
    for class_record in class_records:
        attendance = AttendanceRecord.query.filter_by(
            class_record_id=class_record.id,
            student_id=student_id
        ).first()
        
        if not attendance:
            print(f'[SYNC] No attendance found for class_record_id={class_record.id}, student_id={student_id}', flush=True)
            continue
        
        print(f'[SYNC] Attendance status for class_record_id={class_record.id}: {attendance.status}', flush=True)
        
        if attendance.status == '出勤':
            attendance.status = '请假'
            attendance.updated_at = db.func.now()
            
            student_course = StudentCourse.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first()
            
            if student_course:
                student_course.remaining_hours += float(class_record.hours)
                hours_restored += float(class_record.hours)
            
            updated_count += 1
    
    print(f'[SYNC] Updated {updated_count} records, restored {hours_restored} hours', flush=True)
    
    return {
        'updated_count': updated_count,
        'hours_restored': hours_restored
    }

def sync_leave_on_record_creation(class_record):
    """
    录入上课记录时，检查学生是否有已批准的请假记录
    
    逻辑：
    1. 获取该班级的所有学生
    2. 检查每个学生在该课程、该日期是否有已批准的请假记录
    3. 如果有，考勤状态自动设为'请假'；否则设为'出勤'
    
    这个函数在创建上课记录时调用，确保提前请假的学生被正确标记
    """
    from models import ClassRecord, AttendanceRecord, LeaveRecord, StudentCourse, Class, Student
    
    class_id = class_record.class_id
    course_id = class_record.course_id
    class_date = class_record.class_date
    
    class_ = Class.query.get(class_id)
    if not class_:
        return
    
    students = [cs.student for cs in class_.class_students]
    
    for student in students:
        is_leave = LeaveRecord.query.filter(
            LeaveRecord.student_id == student.id,
            LeaveRecord.course_id == course_id,
            LeaveRecord.start_date <= class_date,
            LeaveRecord.end_date >= class_date,
            LeaveRecord.status == '已批准'
        ).first()
        
        status = '请假' if is_leave else '出勤'
        
        attendance = AttendanceRecord(
            class_record_id=class_record.id,
            student_id=student.id,
            status=status
        )
        db.session.add(attendance)
        
        if status == '出勤':
            student_course = StudentCourse.query.filter_by(
                student_id=student.id,
                course_id=course_id
            ).first()
            if student_course and student_course.remaining_hours > 0:
                student_course.remaining_hours -= class_record.hours
