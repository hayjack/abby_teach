from flask import Blueprint, jsonify, request
from models import ClassSchedule, Class, User
from extensions import db
from datetime import datetime


schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/classes/<int:class_id>/schedules', methods=['GET'])
def get_class_schedules(class_id):
    """获取班级的排课列表"""
    try:
        schedules = ClassSchedule.query.filter_by(class_id=class_id).all()
        
        # 为每个排课添加教师信息
        schedules_with_teacher = []
        for schedule in schedules:
            schedule_dict = schedule.to_dict()
            teacher = User.query.get(schedule.teacher_id)
            if teacher:
                schedule_dict['teacher_name'] = teacher.name
            schedules_with_teacher.append(schedule_dict)
        
        return jsonify({'success': True, 'data': schedules_with_teacher})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@schedule_bp.route('/classes/<int:class_id>/schedules', methods=['POST'])
def add_class_schedule(class_id):
    """为班级添加排课"""
    try:
        data = request.get_json()
        
        # 验证参数
        required_fields = ['teacher_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        # 验证班级和教师是否存在
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({'success': False, 'message': '班级不存在'}), 404
        
        teacher = User.query.get(data['teacher_id'])
        if not teacher:
            return jsonify({'success': False, 'message': '教师不存在'}), 404
        
        # 验证时间格式
        try:
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'success': False, 'message': '时间格式错误，应为 HH:MM'}), 400
        
        # 验证时间范围
        if start_time >= end_time:
            return jsonify({'success': False, 'message': '开始时间必须早于结束时间'}), 400
        
        # 验证星期范围
        if data['day_of_week'] < 1 or data['day_of_week'] > 7:
            return jsonify({'success': False, 'message': '星期范围错误，应为 1-7'}), 400
        
        # 检查是否存在时间冲突
        existing_schedules = ClassSchedule.query.filter_by(
            class_id=class_id,
            day_of_week=data['day_of_week']
        ).all()
        
        has_conflict = False
        conflict_schedules = []
        
        for existing in existing_schedules:
            if not (end_time <= existing.start_time or start_time >= existing.end_time):
                has_conflict = True
                conflict_schedules.append(existing)
        
        # 创建排课
        new_schedule = ClassSchedule(
            class_id=class_id,
            teacher_id=data['teacher_id'],
            day_of_week=data['day_of_week'],
            start_time=start_time,
            end_time=end_time,
            is_conflict=has_conflict
        )
        
        db.session.add(new_schedule)
        
        # 更新冲突的排课记录
        for schedule in conflict_schedules:
            schedule.is_conflict = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'data': new_schedule.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@schedule_bp.route('/classes/<int:class_id>/schedules/<int:schedule_id>', methods=['PUT'])
def update_class_schedule(class_id, schedule_id):
    """更新班级排课"""
    try:
        data = request.get_json()
        schedule = ClassSchedule.query.filter_by(id=schedule_id, class_id=class_id).first()
        
        if not schedule:
            return jsonify({'success': False, 'message': '排课不存在'}), 404
        
        # 更新字段
        if 'teacher_id' in data:
            teacher = User.query.get(data['teacher_id'])
            if not teacher:
                return jsonify({'success': False, 'message': '教师不存在'}), 404
            schedule.teacher_id = data['teacher_id']
        
        if 'day_of_week' in data:
            if data['day_of_week'] < 1 or data['day_of_week'] > 7:
                return jsonify({'success': False, 'message': '星期范围错误，应为 1-7'}), 400
            schedule.day_of_week = data['day_of_week']
        
        if 'start_time' in data or 'end_time' in data:
            start_time = schedule.start_time
            end_time = schedule.end_time
            
            if 'start_time' in data:
                try:
                    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                except ValueError:
                    return jsonify({'success': False, 'message': '开始时间格式错误，应为 HH:MM'}), 400
            
            if 'end_time' in data:
                try:
                    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                except ValueError:
                    return jsonify({'success': False, 'message': '结束时间格式错误，应为 HH:MM'}), 400
            
            if start_time >= end_time:
                return jsonify({'success': False, 'message': '开始时间必须早于结束时间'}), 400
            
            # 检查时间冲突
            existing_schedules = ClassSchedule.query.filter_by(
                class_id=class_id,
                day_of_week=schedule.day_of_week
            ).filter(ClassSchedule.id != schedule_id).all()
            
            has_conflict = False
            conflict_schedules = []
            
            for existing in existing_schedules:
                if not (end_time <= existing.start_time or start_time >= existing.end_time):
                    has_conflict = True
                    conflict_schedules.append(existing)
            
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.is_conflict = has_conflict
            
            # 更新冲突的排课记录
            for conflict_schedule in conflict_schedules:
                conflict_schedule.is_conflict = True
        
        # 重新检查所有排课的冲突状态
        all_schedules = ClassSchedule.query.filter_by(class_id=class_id).all()
        for s in all_schedules:
            # 检查该排课是否与其他排课冲突
            other_schedules = ClassSchedule.query.filter_by(
                class_id=class_id,
                day_of_week=s.day_of_week
            ).filter(ClassSchedule.id != s.id).all()
            
            s.is_conflict = False
            for other in other_schedules:
                if not (s.end_time <= other.start_time or s.start_time >= other.end_time):
                    s.is_conflict = True
                    break
        
        db.session.commit()
        return jsonify({'success': True, 'data': schedule.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@schedule_bp.route('/classes/<int:class_id>/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_class_schedule(class_id, schedule_id):
    """删除班级排课"""
    try:
        schedule = ClassSchedule.query.filter_by(id=schedule_id, class_id=class_id).first()
        
        if not schedule:
            return jsonify({'success': False, 'message': '排课不存在'}), 404
        
        deleted_day_of_week = schedule.day_of_week
        db.session.delete(schedule)
        
        # 重新检查所有排课的冲突状态
        all_schedules = ClassSchedule.query.filter_by(class_id=class_id).all()
        for s in all_schedules:
            # 检查该排课是否与其他排课冲突
            other_schedules = ClassSchedule.query.filter_by(
                class_id=class_id,
                day_of_week=s.day_of_week
            ).filter(ClassSchedule.id != s.id).all()
            
            s.is_conflict = False
            for other in other_schedules:
                if not (s.end_time <= other.start_time or s.start_time >= other.end_time):
                    s.is_conflict = True
                    break
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@schedule_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """获取课程表数据，支持按教师、班级、排课日期和排课时间进行筛选"""
    try:
        # 获取查询参数
        teacher_id = request.args.get('teacher_id', type=int)
        class_id = request.args.get('class_id', type=int)
        day_of_week = request.args.get('day_of_week', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        # 构建查询
        query = ClassSchedule.query
        
        # 应用筛选条件
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        if class_id:
            query = query.filter_by(class_id=class_id)
        if day_of_week:
            query = query.filter_by(day_of_week=day_of_week)
        if start_time:
            try:
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                query = query.filter(ClassSchedule.start_time >= start_time_obj)
            except ValueError:
                pass
        if end_time:
            try:
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
                query = query.filter(ClassSchedule.end_time <= end_time_obj)
            except ValueError:
                pass
        
        # 排序：按排课日期（周一到周日），排课时间由小到大
        query = query.order_by(ClassSchedule.day_of_week, ClassSchedule.start_time)
        
        # 执行查询
        schedules = query.all()
        
        # 为每个排课添加教师、班级和课程信息
        schedules_with_info = []
        for schedule in schedules:
            schedule_dict = schedule.to_dict()
            
            # 添加教师信息
            teacher = User.query.get(schedule.teacher_id)
            if teacher:
                schedule_dict['teacher_name'] = teacher.name
            
            # 添加班级信息
            cls = Class.query.get(schedule.class_id)
            if cls:
                schedule_dict['class_name'] = cls.name
            
            # 添加课程信息
            from models import ClassCourse, Course
            class_courses = ClassCourse.query.filter_by(class_id=schedule.class_id).all()
            if class_courses:
                # 假设每个班级只有一个课程，实际可根据业务逻辑调整
                course = Course.query.get(class_courses[0].course_id)
                if course:
                    schedule_dict['course_name'] = course.name
                else:
                    schedule_dict['course_name'] = ''
            else:
                schedule_dict['course_name'] = ''
            
            schedules_with_info.append(schedule_dict)
        
        return jsonify({'success': True, 'data': schedules_with_info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
