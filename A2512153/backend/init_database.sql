CREATE DATABASE IF NOT EXISTS elderly_care CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE elderly_care;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar VARCHAR(255),
    role ENUM('admin', 'service_provider', 'elderly', 'family_member') DEFAULT 'elderly',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_is_active (is_active),
    INDEX idx_users_username (username),
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS service_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_categories_sort (sort_order),
    INDEX idx_categories_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INT,
    provider_id INT,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) DEFAULT '次',
    image VARCHAR(255),
    images TEXT,
    service_time VARCHAR(100),
    location VARCHAR(255),
    rating DECIMAL(3,2) DEFAULT 0.0,
    review_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_services_category (category_id),
    INDEX idx_services_provider (provider_id),
    INDEX idx_services_rating (rating DESC),
    INDEX idx_services_price (price),
    INDEX idx_services_active (is_active),
    FOREIGN KEY (category_id) REFERENCES service_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    contact_name VARCHAR(50) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    detail_address VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_addresses_user (user_id),
    INDEX idx_addresses_default (is_default),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    provider_id INT NOT NULL,
    quantity INT DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'refunded', 'failed') DEFAULT 'pending',
    appointment_date DATETIME,
    address_id INT,
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_orders_user (user_id),
    INDEX idx_orders_service (service_id),
    INDEX idx_orders_provider (provider_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_payment_status (payment_status),
    INDEX idx_orders_created (created_at DESC),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT,
    FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_no VARCHAR(50) UNIQUE NOT NULL,
    payment_method VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'paid', 'refunded', 'failed') DEFAULT 'pending',
    transaction_id VARCHAR(100),
    paid_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_payments_order (order_id),
    INDEX idx_payments_status (status),
    INDEX idx_payments_transaction (transaction_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    images TEXT,
    reply TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reviews_user (user_id),
    INDEX idx_reviews_service (service_id),
    INDEX idx_reviews_order (order_id),
    INDEX idx_reviews_rating (rating),
    INDEX idx_reviews_created (created_at DESC),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE reviews;
TRUNCATE TABLE payments;
TRUNCATE TABLE orders;
TRUNCATE TABLE addresses;
TRUNCATE TABLE services;
TRUNCATE TABLE service_categories;
TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO users (username, email, phone, hashed_password, full_name, role, is_active) VALUES
('admin', 'admin@example.com', '13800000001', '123456', '系统管理员', 'admin', TRUE),
('provider1', 'provider1@example.com', '13800000002', '123456', '张护理', 'service_provider', TRUE),
('provider2', 'provider2@example.com', '13800000003', '123456', '李医生', 'service_provider', TRUE),
('provider3', 'provider3@example.com', '13800000004', '123456', '王厨师', 'service_provider', TRUE),
('elderly1', 'elderly1@example.com', '13800000005', '123456', '刘大爷', 'elderly', TRUE),
('elderly2', 'elderly2@example.com', '13800000006', '123456', '陈奶奶', 'elderly', TRUE),
('elderly3', 'elderly3@example.com', '13800000008', '123456', '王大爷', 'elderly', TRUE),
('family1', 'family1@example.com', '13800000007', '123456', '刘先生', 'family_member', TRUE),
('family2', 'family2@example.com', '13800000009', '123456', '李女士', 'family_member', TRUE);

INSERT INTO service_categories (name, description, icon, sort_order, is_active) VALUES
('居家护理', '专业护理人员上门提供日常生活照护', '🏠', 1, TRUE),
('医疗服务', '定期体检、慢病管理、康复治疗等', '⚕️', 2, TRUE),
('餐饮服务', '营养配餐、送餐上门服务', '🍱', 3, TRUE),
('家政服务', '家庭清洁、洗衣等家务服务', '🧹', 4, TRUE),
('陪伴服务', '聊天陪伴、户外活动陪同', '👥', 5, TRUE),
('康复理疗', '物理治疗、按摩、针灸等', '💆', 6, TRUE),
('心理咨询', '心理疏导、情感支持', '🧠', 7, TRUE),
('紧急救助', '24小时应急响应服务', '🚨', 8, TRUE);

INSERT INTO services (title, description, category_id, provider_id, price, unit, service_time, location, rating, review_count, is_active) VALUES
('专业居家护理服务', '经验丰富的护理人员提供专业的上门护理服务', 1, 2, 150.00, '次', '2-3小时', '上门服务', 4.8, 125, TRUE),
('日常起居照料', '协助老人完成日常起居活动', 1, 2, 120.00, '次', '2小时', '上门服务', 4.6, 89, TRUE),
('健康体检服务', '专业医生上门进行健康体检', 2, 3, 200.00, '次', '1小时', '上门服务', 4.9, 156, TRUE),
('慢病管理服务', '针对慢性疾病提供定期监测和用药指导', 2, 3, 180.00, '次', '1.5小时', '上门服务', 4.7, 98, TRUE),
('营养配餐服务', '根据老人健康状况提供营养均衡的配餐', 3, 4, 80.00, '天', '全天', '送餐上门', 4.8, 203, TRUE),
('特殊饮食定制', '针对特殊需求提供专业的饮食定制', 3, 4, 100.00, '天', '全天', '送餐上门', 4.9, 145, TRUE),
('家庭深度清洁', '专业家政人员提供家庭深度清洁服务', 4, 2, 200.00, '次', '3-4小时', '上门服务', 4.7, 167, TRUE),
('日常保洁服务', '定期上门进行日常保洁', 4, 2, 150.00, '次', '2小时', '上门服务', 4.6, 134, TRUE),
('聊天陪伴服务', '专业陪伴人员提供情感陪伴服务', 5, 2, 80.00, '次', '2小时', '上门服务', 4.9, 189, TRUE),
('户外活动陪同', '陪同老人进行户外活动', 5, 2, 100.00, '次', '3小时', '陪同外出', 4.8, 112, TRUE),
('专业按摩服务', '经验丰富的按摩师提供专业的按摩推拿服务', 6, 3, 150.00, '次', '1.5小时', '上门服务', 4.8, 178, TRUE),
('物理康复治疗', '针对术后康复提供专业的物理康复治疗', 6, 3, 200.00, '次', '2小时', '上门服务', 4.7, 95, TRUE),
('心理健康咨询', '专业心理咨询师提供心理健康咨询服务', 7, 3, 180.00, '次', '1.5小时', '上门服务', 4.9, 67, TRUE),
('24小时紧急响应', '提供24小时紧急响应服务', 8, 3, 300.00, '月', '24小时', '电话+上门', 5.0, 45, TRUE);

INSERT INTO addresses (user_id, contact_name, contact_phone, province, city, district, detail_address, is_default) VALUES
(5, '刘大爷', '13800000005', '北京市', '北京市', '朝阳区', '朝阳区建国路88号阳光小区3号楼2单元501室', TRUE),
(5, '刘先生', '13800000007', '北京市', '北京市', '朝阳区', '朝阳区建国路88号阳光小区3号楼2单元501室', FALSE),
(6, '陈奶奶', '13800000006', '上海市', '上海市', '浦东新区', '浦东新区世纪大道1000号金茂大厦A座1205室', TRUE),
(7, '王大爷', '13800000008', '广州市', '广东省', '天河区', '天河区天河路123号天河城A座808室', TRUE),
(8, '刘先生', '13800000007', '北京市', '北京市', '海淀区', '海淀区中关村大街1号海龙大厦10层', FALSE),
(9, '李女士', '13800000009', '深圳市', '广东省', '南山区', '南山区科技园南路1000号科技大厦15层', TRUE);

INSERT INTO orders (order_no, user_id, service_id, provider_id, quantity, total_price, status, payment_status, appointment_date, address_id, remark) VALUES
('ORD202501170001', 5, 1, 2, 1, 150.00, 'completed', 'paid', '2025-01-15 10:00:00', 1, '请准时上门，老人行动不便'),
('ORD202501170002', 5, 3, 3, 1, 200.00, 'confirmed', 'paid', '2025-01-20 14:00:00', 1, '体检前请提前通知'),
('ORD202501170003', 6, 5, 4, 7, 560.00, 'in_progress', 'paid', '2025-01-18 08:00:00', 3, '少盐少油，清淡饮食'),
('ORD202501170004', 5, 9, 2, 1, 80.00, 'pending', 'pending', '2025-01-22 15:00:00', 1, NULL),
('ORD202501170005', 7, 2, 2, 2, 240.00, 'completed', 'paid', '2025-01-16 09:00:00', 4, '需要协助起床和洗漱'),
('ORD202501170006', 6, 7, 2, 1, 200.00, 'confirmed', 'paid', '2025-01-21 10:00:00', 3, '重点清洁厨房和卫生间'),
('ORD202501170007', 7, 11, 3, 1, 150.00, 'pending', 'pending', '2025-01-23 14:00:00', 4, NULL);

INSERT INTO payments (order_id, payment_no, payment_method, amount, status, transaction_id, paid_at) VALUES
(1, 'PAY202501150001', 'alipay', 150.00, 'paid', '202501151000012345', '2025-01-15 09:30:00'),
(2, 'PAY202501160002', 'wechat', 200.00, 'paid', 'wx202501161000012345', '2025-01-16 10:15:00'),
(3, 'PAY202501170003', 'alipay', 560.00, 'paid', '202501171000012345', '2025-01-17 08:00:00'),
(5, 'PAY202501160005', 'alipay', 240.00, 'paid', '202501161000012346', '2025-01-16 08:30:00'),
(6, 'PAY202501200006', 'wechat', 200.00, 'paid', 'wx202501201000012345', '2025-01-20 09:00:00');

INSERT INTO reviews (user_id, service_id, order_id, rating, comment, is_anonymous) VALUES
(5, 1, 1, 5, '护理人员非常专业，态度也很好，老人很满意。服务很周到，下次还会选择。', FALSE),
(5, 3, 2, 5, '医生很专业，检查很仔细，还给了很多健康建议，非常满意！', FALSE),
(6, 5, 3, 5, '配餐很营养，味道也不错，老人很喜欢。送餐也很及时，服务很好。', FALSE),
(7, 2, 5, 4, '护理人员很细心，服务态度好，就是时间稍微有点短。', FALSE),
(6, 7, 6, 5, '清洁得很彻底，家里焕然一新，非常满意！', FALSE);

UPDATE services s
SET 
    s.rating = (SELECT AVG(r.rating) FROM reviews r WHERE r.service_id = s.id),
    s.review_count = (SELECT COUNT(*) FROM reviews r WHERE r.service_id = s.id)
WHERE s.id IN (SELECT DISTINCT service_id FROM reviews);
