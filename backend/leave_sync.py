from extensions import db
from datetime import date
import logging

logger = logging.getLogger(__name__)

def reconcile_student_hours(student_id, course_id):
    """
    根据考勤记录重新计算学生剩余课时（幂等操作）
    
    逻辑：
    1. 找出该学生该课程的所有上课记录
    2. 找出该学生加入班级的时间
    3. 只统计学生加入班级后、且'出勤'状态的课时总和
    4. 剩余课时 = 总课时 - 已消耗课时
    
    这个函数保证数据一致性，无论之前发生过多少次操作，
    最终结果都只取决于当前的考勤状态和学生加入时间。
    
    注意：如果学生已从班级移除，仍会保留历史课时记录，
    但不会影响已有的考勤和请假记录。
    """
    from models import StudentCourse, ClassRecord, AttendanceRecord, ClassStudent
    
    student_course = StudentCourse.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    
    if not student_course:
        logger.warning(f'[课时] 未找到学生ID={student_id} 课程ID={course_id} 的选课记录')
        return
    
    # 找出该学生该课程的所有上课记录
    class_records = ClassRecord.query.filter_by(course_id=course_id).all()
    
    # 找出该学生加入班级的时间
    class_student = None
    if class_records:
        # 尝试查找学生在第一个上课记录所属班级的记录
        class_student = ClassStudent.query.filter_by(
            student_id=student_id,
            class_id=class_records[0].class_id
        ).first()
    
    join_date = class_student.join_date if class_student else None
    logger.info(f'[课时] 学生ID={student_id} 加入班级时间: {join_date}')
    
    # 计算已消耗的课时（只统计出勤的记录，且在学生加入班级之后）
    consumed_hours = 0.0
    for cr in class_records:
        # 检查上课日期是否在学生加入班级之后
        # 如果学生已从班级移除（join_date为None），则统计所有出勤记录
        if join_date and cr.class_date < join_date:
            logger.debug(f'[课时] 跳过上课记录ID={cr.id}，上课日期 {cr.class_date} 在学生加入日期 {join_date} 之前')
            continue
            
        attendance = AttendanceRecord.query.filter_by(
            class_record_id=cr.id,
            student_id=student_id
        ).first()
        
        if attendance and attendance.status == '出勤':
            consumed_hours += float(cr.hours)
    
    # 重新计算剩余课时
    old_remaining = student_course.remaining_hours
    student_course.remaining_hours = float(student_course.total_hours) - consumed_hours
    
    logger.info(f'[课时] 重新计算: student_id={student_id}, course_id={course_id}, 总课时={student_course.total_hours}, 已消耗={consumed_hours}, 剩余: {old_remaining} -> {student_course.remaining_hours}')

def sync_attendance_with_leave(leave_record):
    """
    请假审批通过后，联动更新考勤记录
    
    逻辑：
    1. 查找该学生在请假时间段内、对应课程的所有上课记录
    2. 将这些上课记录中的考勤状态从'出勤'更新为'请假'
    3. 重新计算剩余课时（确保数据一致性）
    
    支持两种场景：
    - 提前请假：录入上课记录时已标记为请假（无需更新）
    - 课后补假：已将状态标记为出勤，需更新为请假并恢复课时
    """
    from models import ClassRecord, AttendanceRecord, StudentCourse
    
    logger.info(f'[联动] 开始处理请假联动: leave_id={leave_record.id}, student_id={leave_record.student_id}, course_id={leave_record.course_id}')
    logger.info(f'[联动] 请假日期范围: {leave_record.start_date} 至 {leave_record.end_date}')
    
    student_id = leave_record.student_id
    course_id = leave_record.course_id
    start_date = leave_record.start_date
    end_date = leave_record.end_date
    
    # 查找该学生在请假时间段内的所有上课记录
    class_records = ClassRecord.query.filter(
        ClassRecord.course_id == course_id,
        ClassRecord.class_date >= start_date,
        ClassRecord.class_date <= end_date
    ).all()
    
    logger.info(f'[联动] 找到 {len(class_records)} 条上课记录')
    
    updated_count = 0
    
    for class_record in class_records:
        # 查找该学生在该上课记录中的考勤记录
        attendance = AttendanceRecord.query.filter_by(
            class_record_id=class_record.id,
            student_id=student_id
        ).first()
        
        if not attendance:
            logger.warning(f'[联动] 上课记录ID={class_record.id} 中没有该学生的考勤记录，跳过')
            continue
        
        logger.info(f'[联动] 上课记录ID={class_record.id}, 当前考勤状态={attendance.status}')
        
        # 如果当前状态是'出勤'，需要更新为'请假'
        if attendance.status == '出勤':
            logger.info(f'[联动] 更新考勤状态: 出勤 -> 请假')
            attendance.status = '请假'
            attendance.updated_at = db.func.now()
            updated_count += 1
        else:
            logger.info(f'[联动] 考勤状态为 {attendance.status}，无需更新')
    
    # 重新计算剩余课时（幂等操作，确保数据一致性）
    reconcile_student_hours(student_id, course_id)
    
    # 获取更新后的课时用于返回
    student_course = StudentCourse.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    hours_restored = 0
    if student_course:
        # 计算恢复的课时（基于考勤状态变化）
        for class_record in class_records:
            attendance = AttendanceRecord.query.filter_by(
                class_record_id=class_record.id,
                student_id=student_id
            ).first()
            if attendance and attendance.status == '请假':
                hours_restored += float(class_record.hours)
    
    logger.info(f'[联动] 联动完成: 更新 {updated_count} 条考勤记录，恢复 {hours_restored} 课时')
    
    return {
        'updated_count': updated_count,
        'hours_restored': hours_restored
    }

def sync_leave_on_record_creation(class_record):
    """
    录入上课记录时，检查学生是否有已批准的请假记录
    
    逻辑：
    1. 获取该班级的所有学生
    2. 只处理加入班级时间小于等于上课时间的学生
    3. 检查每个学生在该课程、该日期是否有已批准的请假记录
    4. 如果有，考勤状态自动设为'请假'；否则设为'出勤'
    5. 创建考勤记录后，重新计算课时（确保数据一致性）
    
    这个函数在创建上课记录时调用，确保提前请假的学生被正确标记
    """
    from models import ClassRecord, AttendanceRecord, LeaveRecord, StudentCourse, Class, Student, ClassStudent
    
    logger.info(f'[考勤] 开始创建考勤记录: class_record_id={class_record.id}, class_id={class_record.class_id}, course_id={class_record.course_id}, date={class_record.class_date}')
    
    class_id = class_record.class_id
    course_id = class_record.course_id
    class_date = class_record.class_date
    
    class_ = Class.query.get(class_id)
    if not class_:
        logger.error(f'[考勤] 班级ID={class_id} 不存在')
        return
    
    # 获取班级的所有学生（包含加入时间）
    class_students = class_.class_students
    logger.info(f'[考勤] 班级共有 {len(class_students)} 名学生')
    
    students_to_process = []
    
    for cs in class_students:
        # 检查学生加入班级的时间是否小于等于上课时间
        join_date = cs.join_date
        if join_date and join_date > class_date:
            logger.info(f'[考勤] 跳过学生 {cs.student.name}(ID={cs.student.id})，加入日期 {join_date} 在上课日期 {class_date} 之后')
            continue
        students_to_process.append(cs)
    
    logger.info(f'[考勤] 符合条件的学生数: {len(students_to_process)}')
    
    for cs in students_to_process:
        student = cs.student
        # 检查是否有已批准的请假记录覆盖该日期
        is_leave = LeaveRecord.query.filter(
            LeaveRecord.student_id == student.id,
            LeaveRecord.course_id == course_id,
            LeaveRecord.start_date <= class_date,
            LeaveRecord.end_date >= class_date,
            LeaveRecord.status == '已批准'
        ).first()
        
        status = '请假' if is_leave else '出勤'
        
        if is_leave:
            logger.info(f'[考勤] 学生 {student.name}(ID={student.id}) 有请假记录，标记为请假')
        else:
            logger.debug(f'[考勤] 学生 {student.name}(ID={student.id}) 无请假记录，标记为出勤')
        
        # 创建考勤记录
        attendance = AttendanceRecord(
            class_record_id=class_record.id,
            student_id=student.id,
            status=status
        )
        db.session.add(attendance)
    
    # 为符合条件的学生重新计算课时（幂等操作，确保数据一致性）
    for cs in students_to_process:
        reconcile_student_hours(cs.student.id, course_id)
    
    logger.info(f'[考勤] 考勤记录创建完成，课时已重新计算')

def cancel_leave_sync(leave_record):
    """
    删除已批准的请假记录时，联动恢复考勤和课时
    
    逻辑：
    1. 查找该学生在请假时间段内、对应课程的所有上课记录
    2. 将这些上课记录中的考勤状态从'请假'恢复为'出勤'
    3. 重新计算剩余课时（根据上课记录的课时重新扣除）
    
    注意：只对'已批准'状态的请假记录执行联动，
    '待审批'和'已拒绝'的请假记录不影响考勤和课时。
    """
    from models import ClassRecord, AttendanceRecord, StudentCourse
    
    logger.info(f'[联动-撤销] 开始处理请假撤销联动: leave_id={leave_record.id}, student_id={leave_record.student_id}, course_id={leave_record.course_id}')
    logger.info(f'[联动-撤销] 请假日期范围: {leave_record.start_date} 至 {leave_record.end_date}')
    
    student_id = leave_record.student_id
    course_id = leave_record.course_id
    start_date = leave_record.start_date
    end_date = leave_record.end_date
    
    # 查找该学生在请假时间段内的所有上课记录
    class_records = ClassRecord.query.filter(
        ClassRecord.course_id == course_id,
        ClassRecord.class_date >= start_date,
        ClassRecord.class_date <= end_date
    ).all()
    
    logger.info(f'[联动-撤销] 找到 {len(class_records)} 条上课记录')
    
    updated_count = 0
    
    for class_record in class_records:
        # 查找该学生在该上课记录中的考勤记录
        attendance = AttendanceRecord.query.filter_by(
            class_record_id=class_record.id,
            student_id=student_id
        ).first()
        
        if not attendance:
            logger.warning(f'[联动-撤销] 上课记录ID={class_record.id} 中没有该学生的考勤记录，跳过')
            continue
        
        logger.info(f'[联动-撤销] 上课记录ID={class_record.id}, 当前考勤状态={attendance.status}')
        
        # 如果当前状态是'请假'，需要恢复为'出勤'
        if attendance.status == '请假':
            logger.info(f'[联动-撤销] 恢复考勤状态: 请假 -> 出勤')
            attendance.status = '出勤'
            attendance.updated_at = db.func.now()
            updated_count += 1
        else:
            logger.info(f'[联动-撤销] 考勤状态为 {attendance.status}，无需更新')
    
    # 重新计算剩余课时（幂等操作，确保数据一致性）
    reconcile_student_hours(student_id, course_id)
    
    # 获取更新后的课时用于返回
    student_course = StudentCourse.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()
    hours_deducted = 0
    if student_course:
        # 计算需要扣除的课时（基于考勤状态变化）
        for class_record in class_records:
            attendance = AttendanceRecord.query.filter_by(
                class_record_id=class_record.id,
                student_id=student_id
            ).first()
            if attendance and attendance.status == '出勤':
                hours_deducted += float(class_record.hours)
    
    logger.info(f'[联动-撤销] 联动完成: 更新 {updated_count} 条考勤记录，扣除 {hours_deducted} 课时')
    
    return {
        'updated_count': updated_count,
        'hours_deducted': hours_deducted
    }
