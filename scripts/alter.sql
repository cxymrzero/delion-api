ALTER TABLE `nft` ADD COLUMN `total_num` SMALLINT NOT NULL;
ALTER TABLE `nft` ADD COLUMN `ac_num` SMALLINT NOT NULL;
ALTER TABLE `nft` ADD COLUMN `check_num` SMALLINT NOT NULL;
ALTER TABLE `nft` MODIFY `aff_id` int(11) NULL;
ALTER TABLE `nft` MODIFY `aff_group_id` int(11) NULL;
ALTER TABLE `nft` MODIFY `user_id` int(11) NULL;
ALTER TABLE `nft_user_rel` MODIFY `sender_id` int(11) NULL;
ALTER TABLE `nft_user_rel` ADD COLUMN `content` VARCHAR(256) NOT NULL;