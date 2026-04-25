# 教学Web系统数据库ER图

## 表关系图

```
+------------------+       +------------------+       +------------------+
|      users       |       |      roles       |       |      menus       |
+------------------+       +------------------+       +------------------+
| id (PK)          |<--+   | id (PK)          |<--+   | id (PK)          |
| username         |   |   | name             |   |   | name             |
| password         |   |   +------------------+   |   | path             |
| name             |   |                         |   | parent_id (FK)   |
| english_name     |   |                         |   | icon             |
| phone            |   |                         |   | order            |
| role_id (FK)     +---+                         |   +------------------+
| created_at       |                             |           ^
| updated_at       |                             |           |
+------------------+                             |           |
                                                 |           |
+------------------+       +------------------+  |           |
|     students     |       |  role_menus      |--+           |
+------------------+       +------------------+              |
| id (PK)          |       | id (PK)          |              |
| name             |       | role_id (FK)     |              |
| english_name     |       | menu_id (FK)     +--------------+
| gender           |       +------------------+              
| birthday         |                                         
| parent_name      |                                         
| parent_phone     |                                         
| address          |                                         
| created_at       |                                         
| updated_at       |                                         
+------------------+                                         
        ^                                                    
        |                                                    
        |                                                    
+------------------+       +------------------+              
| payment_records  |       | student_courses  |              
+------------------+       +------------------+              
| id (PK)          |       | id (PK)          |              
| student_id (FK)  +-------+ student_id (FK)  |              
| amount           |       | course_id (FK)   |              
| payment_date     |       | total_hours      |              
| payment_type     |       | remaining_hours  |              
| remark           |       | start_date       |              
| created_at       |       | end_date         |              
| updated_at       |       | created_at       |              
+------------------+       | updated_at       |              
                           +------------------+              
                                  ^                         
                                  |                         
+------------------+       +------------------+              
|     classes      |       |     courses      |              
+------------------+       +------------------+              
| id (PK)          |       | id (PK)          |              
| name             |       | name             |              
| description      |       | description      |              
| start_date       |       | total_hours      |              
| end_date         |       | price            |              
| created_at       |       | created_at       |              
| updated_at       |       | updated_at       |              
+------------------+       +------------------+              
        ^                         ^                         
        |                         |                         
+------------------+       +------------------+              
| class_students   |       | class_courses    |              
+------------------+       +------------------+              
| id (PK)          |       | id (PK)          |              
| class_id (FK)    +-------+ class_id (FK)    |              
| student_id (FK)  |       | course_id (FK)   +--------------+
| join_date        |       | created_at       |              
| created_at       |       | updated_at       |              
| updated_at       |       +------------------+              
+------------------+                                         
        ^                                                    
        |                                                    
+------------------+       +------------------+              
| class_teachers   |       | class_records    |              
+------------------+       +------------------+              
| id (PK)          |       | id (PK)          |              
| class_id (FK)    +-------+ class_id (FK)    |              
| teacher_id (FK)  |       | course_id (FK)   |              
| created_at       |       | teacher_id (FK)  |              
| updated_at       |       | class_date       |              
+------------------+       | start_time       |              
                           | end_time         |              
                           | hours            |              
                           | content          |              
                           | created_at       |              
                           | updated_at       |              
                           +------------------+              
                                  ^                         
                                  |                         
+------------------+       +------------------+              
| leave_records    |       | attendance_records|              
+------------------+       +------------------+              
| id (PK)          |       | id (PK)          |              
| student_id (FK)  +-------+ student_id (FK)  |              
| course_id (FK)   |       | class_record_id (FK)+-----------+
| start_date       |       | status           |              
| end_date         |       | created_at       |              
| reason           |       | updated_at       |              
| status           |       +------------------+              
| created_at       |                                         
| updated_at       |                                         
+------------------+                                         
```

## 表关系说明

1. **用户与角色关系**：一个用户属于一个角色，一个角色可以有多个用户。
2. **角色与菜单关系**：一个角色可以有多个菜单权限，一个菜单可以被多个角色拥有（多对多关系）。
3. **学生与缴费记录关系**：一个学生可以有多个缴费记录，一个缴费记录属于一个学生。
4. **学生与课程关系**：一个学生可以学习多个课程，一个课程可以有多个学生（多对多关系，通过student\_courses表关联）。
5. **班级与学生关系**：一个班级可以有多个学生，一个学生可以属于多个班级（多对多关系，通过class\_students表关联）。
6. **班级与教师关系**：一个班级可以有多个教师，一个教师可以教多个班级（多对多关系，通过class\_teachers表关联）。
7. **班级与课程关系**：一个班级可以开设多个课程，一个课程可以在多个班级开设（多对多关系，通过class\_courses表关联）。
8. **上课记录与班级、课程、教师关系**：一个上课记录属于一个班级、一个课程和一个教师。
9. **考勤记录与上课记录、学生关系**：一个考勤记录属于一个上课记录和一个学生。
10. **请假记录与学生、课程关系**：一个请假记录属于一个学生和一个课程。

## 数据库设计特点

1. **规范化设计**：遵循数据库设计的规范化原则，减少数据冗余，提高数据一致性。
2. **关系明确**：通过外键约束确保表之间的关系完整性。
3. **扩展性**：表结构设计考虑了系统的可扩展性，方便后续功能的添加和修改。
4. **性能优化**：合理设计索引，提高查询效率。
5. **安全性**：对敏感数据（如密码）进行加密存储。

## 数据库初始化建议

1. 首先创建基础表：users、roles、menus、role\_menus
2. 然后创建核心业务表：students、courses、classes
3. 接着创建关联表：class\_students、class\_teachers、class\_courses、student\_courses
4. 最后创建业务操作表：payment\_records、class\_records、attendance\_records、leave\_records
5. 初始化数据：
   - 创建默认角色（如管理员、教师）
   - 创建默认菜单
   - 创建默认管理员用户
   - 创建基础课程和班级

这样的数据库设计能够满足教学系统的功能需求，支持教师管理、学生管理、班级管理、课程管理、上课记录、请假记录和报表统计等功能。
