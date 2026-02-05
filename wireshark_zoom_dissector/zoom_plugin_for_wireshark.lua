zoom_o = Proto("zoom_o", "Zoom SFU Encapsulation")
zoom_o.fields.type = ProtoField.new("Type", "zoom_o.type", ftypes.UINT8)
zoom_o.fields.seq = ProtoField.new("Sequence number", "zoom_o.seq", ftypes.UINT16)
zoom_o.fields.ts = ProtoField.new("Timestamp (relative)", "zoom_o.ts", ftypes.UINT32)
zoom_o.fields.control_type = ProtoField.new("Control type", "zoom_o.control_type", ftypes.UINT16)
zoom_o.fields.room = ProtoField.new("Room ID", "zoom_o.id", ftypes.UINT16)
zoom_o.fields.id = ProtoField.new("Unique ID (IP:PORT)", "zoom_o.field", ftypes.UINT16)
zoom_o.fields.cont = ProtoField.new("Cont", "zoom_o.cont", ftypes.UINT8)
zoom_o.fields.hash = ProtoField.new("Unique hash", "zoom_o.hash", ftypes.BYTES)
zoom_o.fields.dir = ProtoField.new("Direction", "zoom_o.dir", ftypes.UINT8)
zoom_o.fields.field = ProtoField.new("Field (Unknown)", "zoom_o.field", ftypes.BYTES)
zoom_o.fields.payload = ProtoField.new("Payload (Unknown)", "zoom_o.payload", ftypes.BYTES)

zoom = Proto("zoom", "Zoom Media Encapsulation")
zoom.fields.type = ProtoField.new("Type", "zoom.type", ftypes.UINT8)
zoom.fields.seq = ProtoField.new("Sequence number", "zoom.seq", ftypes.UINT16)
zoom.fields.ts = ProtoField.new("Timestamp", "zoom.ts", ftypes.UINT32)
zoom.fields.frame_num = ProtoField.new("Frame number", "zoom.frame_num", ftypes.UINT16)
zoom.fields.frame_pkt_count = ProtoField.new("Packets in frame", "zoom.frame_pkt_count", ftypes.UINT8)

zoom.fields.field = ProtoField.new("Field (Unknown)", "zoom.field", ftypes.BYTES)
zoom.fields.cont = ProtoField.new("Cont", "zoom.cont", ftypes.UINT8)
zoom.fields.ssrc = ProtoField.new("SSRC", "zoom.ssrc", ftypes.BYTES)
zoom.fields.media_type = ProtoField.new("Media type", "zoom.media_type", ftypes.UINT8)
zoom.fields.hash = ProtoField.new("Unique hash", "zoom.hash", ftypes.BYTES)
zoom.fields.data_bind_replace_flag = ProtoField.new("Data bind replace flag", "zoom.data_bind_replace_flag", ftypes.BYTES)
zoom.fields.mc35 = ProtoField.new("MC35", "zoom.mc35", ftypes.BYTES)

zoom.fields.field1 = ProtoField.uint8("zoom.field1", "Field1 (Unknown)", base.DEC)
zoom.fields.field2 = ProtoField.uint32("zoom.field2", "Field2 (Unknown)", base.HEX)
zoom.fields.field3 = ProtoField.uint32("zoom.field3", "Field3 (Unknown)", base.HEX)
zoom.fields.data = ProtoField.bytes("zoom.data", "Data (Unknown)")
zoom.fields.num = ProtoField.uint8("zoom.num", "Number (Unknown)", base.DEC)

zoom.fields.t13ts = ProtoField.new("T13 Timestamp", "zoom.t13ts", ftypes.UINT16)
zoom.fields.t13s = ProtoField.new("T13 Sequence number", "zoom.t13s", ftypes.UINT16)
zoom.fields.t13t = ProtoField.new("T13 Subtype", "zoom.t13t", ftypes.UINT8)

zoom.fields.t32_sender = ProtoField.new("Video Sender", "zoom.t32_sender", ftypes.BYTES)
zoom.fields.t32_viewer = ProtoField.new("Video Viewer", "zoom.t32_viewer", ftypes.BYTES)
zoom.fields.t32_field1 = ProtoField.new("T32 Field1 (Unknown)", "zoom.t32_field1", ftypes.BYTES)
zoom.fields.t32_sender_rep = ProtoField.new("Video Sender (rep)", "zoom.t32_sender_rep", ftypes.BYTES)
zoom.fields.t32_quality = ProtoField.new("Video Quality", "zoom.t32_quality", ftypes.UINT8)
zoom.fields.t32_field2 = ProtoField.new("T32 Field2 (Unknown)", "zoom.t32_field2", ftypes.BYTES)
zoom.fields.t32_seq1 = ProtoField.new("Sequence Number 1", "zoom.t32_seq1", ftypes.UINT16)
zoom.fields.t32_seq2 = ProtoField.new("Sequence Number 2", "zoom.t32_seq2", ftypes.UINT16)
zoom.fields.t32_num = ProtoField.new("T32 Number (Unknown)", "zoom.t32_num", ftypes.UINT8)
zoom.fields.t32_data = ProtoField.new("T32 Data", "zoom.t32_data", ftypes.BYTES)


zoom_t21 = Proto("zoom_t21", "Zoom Type21")
zoom_t21.fields.type = ProtoField.new("Zoom Type21 Subtype", "zoom_t21.type", ftypes.UINT8)
zoom_t21.fields.num = ProtoField.new("Number of Subfields", "zoom_t21.num", ftypes.UINT8)

subtype2Proto = {}
for i = 0, 63, 1 do
    subtype2Proto[i] = ProtoField.new("Missing Sequence Number", "zoom_t21.seq" .. i, ftypes.UINT16)
    table.insert(zoom_t21.fields, subtype2Proto[i])
end

subtype3Proto = {}
for i = 0, 63, 1 do
    subtype3Proto[i] = ProtoField.new("Received Frame Number", "zoom_t21.frame" .. i, ftypes.UINT16)
    table.insert(zoom_t21.fields, subtype3Proto[i])
end

zoom_t21_sub = Proto("zoom_t21_sub", "Zoom Type21 Subfield")
zoom_t21_sub.fields.id = ProtoField.new("Media Type", "zoom_t21_sub.id", ftypes.UINT8)

zoom_t21_sub.fields.uf1 = ProtoField.new("Unknown Field 1", "zoom_t21_sub.uf1", ftypes.UINT8)
zoom_t21_sub.fields.uf2 = ProtoField.new("Unknown Field 2", "zoom_t21_sub.uf2", ftypes.UINT8)
zoom_t21_sub.fields.interval = ProtoField.new("Interval (ms)", "zoom_t21_sub.interval", ftypes.UINT32)
zoom_t21_sub.fields.bandwidth = ProtoField.new("Bandwidth (bytes/s)", "zoom_t21_sub.bandwidth", ftypes.UINT32)
zoom_t21_sub.fields.recvpktcount = ProtoField.new("Received packet count", "zoom_t21_sub.recv_pktcount", ftypes.UINT8)
zoom_t21_sub.fields.droppktcount = ProtoField.new("Dropped packet count", "zoom_t21_sub.dropp_pktcount", ftypes.UINT8)
zoom_t21_sub.fields.totalpktcount = ProtoField.new("Total packet count", "zoom_t21_sub.total_pktcount", ftypes.UINT8)

zoom_t21_sub.fields.lastrecvts = ProtoField.new("Last received timestamp", "zoom_t21_sub.lastrecvts", ftypes.UINT32)
zoom_t21_sub.fields.suffix = ProtoField.new("Length of Suffix", "zoom_t21_sub.suffix", ftypes.UINT8)

zoom_video = Proto("zoom_video", "Zoom Video RTP Extension")
zoom_video.fields.quality = ProtoField.new("Video Quality", "zoom_video.quality", ftypes.UINT8)
zoom_video.fields.seq1 = ProtoField.new("Sequence Number 1", "zoom_video.seq1", ftypes.UINT16)
zoom_video.fields.seq2 = ProtoField.new("Sequence Number 2", "zoom_video.seq2", ftypes.UINT16)


function get_type_desc(type)
    local desc = "Unknown"

    if type == 13 then
        desc = "Screen Share"
    elseif type == 15 then
        desc = "Audio"
    elseif type == 16 then
        desc = "Video"
    elseif type == 30 then
        desc = "Screen Share"
    elseif type == 32 then
        desc = "ZOOM_T32"
    elseif type == 33 or type == 35 then
        desc = "RTCP-SR"
	elseif type == 34 then
		desc = "RTCP-SRSD"
    end

    return desc
end

function get_zoom_o_dir_desc(dir)
    local desc = "Unknown"

    if dir == 0 then
        desc = "to Zoom"
    elseif dir == 4 then
        desc = "from Zoom"
    end

    return desc
end

function get_zoom_o_type_desc(type)
	local desc = "Unknown"
	if type == 1 then
		desc = "Handshake, To Zoom"
	elseif type == 2 then
		desc = "Handshake, From Zoom"
	elseif type == 3 then
		desc = "Req/Rep"
	elseif type == 4 then
		desc = "Req/Rep"
	elseif type == 7 then
		desc = "To Zoom"
	elseif type == 5 then 
		desc = "Multimedia"
	end

	return desc
end

-- Zoom Video RTP Extension:
function zoom_video.dissector(buf, pkt, tree)
    pkt.cols.protocol = zoom_video.name

    local t = tree:add(zoom_video, buf(), "Zoom Video RTP Extension")
    t:add(zoom_video.fields.quality, bit.band(buf(0, 1):uint(), 3))
    t:add(zoom_video.fields.seq1, buf(1, 2))
    t:add(zoom_video.fields.seq2, buf(3, 2))
end

function zoom_t21.dissector(buf, pkt, tree)
    pkt.cols.protocol = zoom_t21.name
    len = buf:len()
    -- if len > 200 then
	-- 	local n = len/6 - 1
	-- 	local b = 5
	-- 	for i = 1, n, 1 do
	-- 		local val = buf(b, 2):uint()
	-- 		local ssrc = buf(b+2, 4)
	-- 		local t = tree:add(zoom_t21, buf(b, 6))
	-- 		t:set_text(string.format("Zoom T21 %s - %d", ssrc, val))
	-- 		b = b + 6
	-- 	end
		
    --     return end

    local typ = buf(0, 1):uint()

    if typ == 0x00 then
        local t = tree:add(zoom_t21, buf(), "Zoom Type21")
        t:add(zoom_t21.fields.type, typ)
        local n = buf(2, 1):uint()
        local b = 3
        t:add(zoom_t21.fields.num, n)
    
        for i = 1, n, 1 do
            local suf = buf(b + 47, 1):uint()
            Dissector.get("zoom_t21_sub"):call(buf(b, 48 + suf):tvb(), pkt, tree)
            b = b + 48 + suf
        end

    elseif typ == 0x02 then
        local t = tree:add(zoom_t21, buf(), "Zoom Type21")
        t:add(zoom_t21.fields.type, typ)
        local n = buf(4, 1):uint()
        t:add(zoom_t21.fields.num, n):set_text("Number of Sequence Numbers: " .. n)

        for i = 0, n-1, 1 do
            t:add(subtype2Proto[i], buf(5+i*2, 2):uint())
        end

    elseif typ == 0x03 then
        local t = tree:add(zoom_t21, buf(), "Zoom Type21")
        t:add(zoom_t21.fields.type, typ)
        local n = buf(4, 1):uint()
        t:add(zoom_t21.fields.num, n):set_text("Number of Frame Numbers: " .. n)

        for i = 0, n-1, 1 do
            local frame = buf(5+i*6, 2):uint()
            local ssrc = buf(7+i*6, 4):uint()
            t:add(subtype3Proto[i], frame):set_text("Received Frame for 0x" .. string.format("%x", ssrc) .. ": " .. frame)
        end
        
    elseif typ == 0x33 then
        local t = tree:add(zoom_t21, buf(), "Zoom Type21: Dummy")
        t:add(zoom_t21.fields.type, typ)

    elseif typ == 0x35 then
        local t = tree:add(zoom_t21, buf(), "Zoom Type21: bw_level")
        t:add(zoom_t21.fields.type, typ)
    
    else
        local t = tree:add(zoom_t21, buf(), "Zoom Type21: Unknown")
        t:add(zoom_t21.fields.type, typ)
        return end

end

function t21_get_type(id)
    local desc = "unknown"
    if id == 1 then
        desc = "Audio"
    elseif id == 2 then
        desc = "DS"
    elseif id == 3 then
        desc = "Video"
    end
    return desc
end

function zoom_t21_sub.dissector(buf, pkt, tree)
    pkt.cols.protocol = zoom_t21_sub.name
    local t = tree:add(zoom_t21_sub, buf(), "Zoom Type21 Subfield")
    local i = buf(2, 1):uint()
    t:add(zoom_t21_sub.fields.id, buf(2, 1)):append_text(" (" .. t21_get_type(i) .. ")")
    t:add(zoom_t21_sub.fields.interval, buf(4, 4))
    t:add(zoom_t21_sub.fields.bandwidth, buf(8, 4))
    t:add(zoom_t21_sub.fields.totalpktcount, buf(12, 4))
    t:add(zoom_t21_sub.fields.uf2, buf(16, 4))
    t:add(zoom_t21_sub.fields.uf2, buf(20, 4))
    t:add(zoom_t21_sub.fields.uf2, buf(24, 4))
    t:add(zoom_t21_sub.fields.lastrecvts, buf(28, 4))
    t:add(zoom_t21_sub.fields.uf2, buf(32, 4))
    t:add(zoom_t21_sub.fields.recvpktcount, buf(36, 2))
    t:add(zoom_t21_sub.fields.droppktcount, buf(38, 2))
    t:add(zoom_t21_sub.fields.droppktcount, buf(40, 2))
    t:add(zoom_t21_sub.fields.droppktcount, buf(42, 2))
    t:add(zoom_t21_sub.fields.totalpktcount, buf(44, 2))
    t:add(zoom_t21_sub.fields.suffix, buf(47, 1))
end

-- Zoom media encapsulation (inner header):
function zoom.dissector(buf, pkt, tree)
    len = buf:len()
    if len == 0 then return end
    pkt.cols.protocol = zoom.name

    local inner_type = buf(0, 1):uint()

    local t = tree:add(zoom, buf(), "Zoom Media Encapsulation")
    t:add(zoom.fields.type, buf(0, 1)):append_text(" (" .. get_type_desc(inner_type) .. ")")

    if inner_type == 1 then
        --t:add(zoom.fields.seq, buf(9, 2))
        --t:add(zoom.fields.ts, buf(11, 4))
		zoom.dissector(buf(2):tvb(), pkt, tree)
        --Dissector.get("rtp"):call(buf(26):tvb(), pkt, tree)
        
    elseif inner_type == 7 then
		t:add(zoom.fields.field1, buf(1, 1))
        t:add(zoom.fields.field2, buf(2, 4))
        Dissector.get("zoom"):call(buf(7):tvb(), pkt, tree)

	elseif inner_type == 12 then
		t:add(zoom.fields.cont, buf(1, 1))
		t:add(zoom.fields.hash, buf(2, 16))
		t:add(zoom.fields.ssrc, buf(18, 4))
		t:add(zoom.fields.media_type, buf(22, 1))
		t:add(zoom.fields.field, buf(23, 4))
		t:add(zoom.fields.field, buf(27, 4))
		t:add(zoom.fields.field, buf(31, 4))
		t:add(zoom.fields.data_bind_replace_flag, buf(57, 9))
    elseif inner_type == 13 then
		if buf(1, 1):uint() == 0x01 then
			t:add(zoom.fields.cont, buf(1, 1))
			t:add(zoom.fields.hash, buf(2, 16))
	        t:add(zoom.fields.ssrc, buf(18, 4))
			t:add(zoom.fields.media_type, buf(22, 1))
			t:add(zoom.fields.field, buf(23, 4))
			t:add(zoom.fields.field, buf(27, 4))
		else
			t:add(zoom.fields.t13ts, buf(1, 2))
			t:add(zoom.fields.t13s, buf(3, 2))
			t:add(zoom.fields.t13t, buf(7, 1))
			if buf(7, 1):uint() == 0 then
	            zoom.dissector(buf(15):tvb(), pkt, tree)
			else
				zoom.dissector(buf(7):tvb(), pkt, tree)
			end
        end

    elseif inner_type == 15 then
		t:add(zoom.fields.field1, buf(1, 1))
        t:add(zoom.fields.field2, buf(2, 4))
		t:add(zoom.fields.num, buf(5, 1))
        t:add(zoom.fields.data, buf(6, 3))
        t:add(zoom.fields.seq, buf(9, 2))
        t:add(zoom.fields.ts, buf(11, 4))
        Dissector.get("rtp"):call(buf(19):tvb(), pkt, tree)
    elseif inner_type == 16 then
		t:add(zoom.fields.field1, buf(1, 1))
        t:add(zoom.fields.field2, buf(2, 4))
        t:add(zoom.fields.num, buf(5, 1))
        t:add(zoom.fields.data, buf(6, 3))
        t:add(zoom.fields.seq, buf(9, 2))
        t:add(zoom.fields.ts, buf(11, 4))

        if (buf(20, 1):uint() == 0x02) then
            t:add(zoom.fields.frame_num, buf(21, 2))
            t:add(zoom.fields.frame_pkt_count, buf(23, 1))

            if (bit.band(buf(25, 1):uint(), 0x7f) == 0x62) then
                Dissector.get("zoom_video"):call(buf(46, 5):tvb(), pkt, tree)
            end
            Dissector.get("rtp"):call(buf(24):tvb(), pkt, tree)

        else
            Dissector.get("rtp"):call(buf(20):tvb(), pkt, tree)
        end

    elseif inner_type == 21 then -- unclear what this type is
		t:add(zoom.fields.field1, buf(1, 1))
        t:add(zoom.fields.field2, buf(2, 4))
        t:add(zoom.fields.num, buf(5, 1))
        t:add(zoom.fields.data, buf(6, 3))
        Dissector.get("zoom_t21"):call(buf(9):tvb(), pkt, tree)
    elseif inner_type == 30 then -- P2P screen sharing
        t:add(zoom.fields.seq, buf(9, 2))
        t:add(zoom.fields.ts, buf(11, 4))
        Dissector.get("rtp"):call(buf(20):tvb(), pkt, tree)
    elseif inner_type == 32 then -- unclear what this type is
		t:add(zoom.fields.field1, buf(1, 1))
		t:add(zoom.fields.t32_sender, buf(2, 4))
	    t:add(zoom.fields.t32_viewer, buf(6, 4))
		t:add(zoom.fields.t32_field1, buf(10, 3))
		t:add(zoom.fields.t32_sender_rep, buf(13, 4))
	 	t:add(zoom.fields.t32_field2, buf(17, 2))
		t:add(zoom.fields.t32_quality, buf(19, 1))
		t:add(zoom.fields.t32_seq1, buf(20, 2))
		t:add(zoom.fields.t32_seq2, buf(22, 2))
		t:add(zoom.fields.t32_num, buf(24, 1))
		t:add(zoom.fields.t32_data, buf(25, 4))
    elseif inner_type == 33 or inner_type == 34 or inner_type == 35 then
		t:add(zoom.fields.field1, buf(1, 1))
		t:add(zoom.fields.field2, buf(2, 4))
		t:add(zoom.fields.num, buf(5, 1))
		t:add(zoom.fields.field3, buf(6, 4))
		t:add(zoom.fields.data, buf(10, 6))
        Dissector.get("rtcp"):call(buf(16):tvb(), pkt, tree)
    else
        Dissector.get("data"):call(buf(15):tvb(), pkt, tree)
    end
end

-- Zoom server encapsulation (outer header):
function zoom_o.dissector(buf, pkt, tree)
    length = buf:len()
    if length == 0 then return end
    pkt.cols.protocol = zoom_o.name
	local outer_type = buf(0, 1):uint()

    local t = tree:add(zoom_o, buf(), "Zoom SFU Encapsulation")
    t:add(zoom_o.fields.type, buf(0, 1)):append_text(" (" .. get_zoom_o_type_desc(outer_type) .. ")")

	if outer_type == 1 then
		t:add(zoom_o.fields.control_type, buf(1, 2))
		t:add(zoom_o.fields.hash, buf(3, 16))
		t:add(zoom_o.fields.field, buf(19, 8))
		t:add(zoom_o.fields.ts, buf(27, 4))
		t:add(zoom_o.fields.ts, buf(31, 4))
		t:add(zoom_o.fields.field, buf(35, 4))
		t:add(zoom_o.fields.payload, buf(39, 64))
	elseif outer_type == 2 then
		t:add(zoom_o.fields.control_type, buf(1, 2))
        t:add(zoom_o.fields.hash, buf(3, 16))
		t:add(zoom_o.fields.room, buf(19, 2))
        t:add(zoom_o.fields.id, buf(21, 2))
		t:add(zoom_o.fields.ts, buf(23, 4))
		t:add(zoom_o.fields.field, buf(27, 16))
		t:add(zoom_o.fields.cont, buf(43, 1))
	elseif outer_type == 3 then
		t:add(zoom_o.fields.control_type, buf(1, 2))
		t:add(zoom_o.fields.seq, buf(3, 2))
		t:add(zoom_o.fields.ts, buf(5, 4))
		t:add(zoom_o.fields.room, buf(9, 2))
		t:add(zoom_o.fields.id, buf(11, 2))
		t:add(zoom_o.fields.cont, buf(13, 1))
		local cont = buf(13, 1):uint()
        if cont == 1 then
			local inner_t = buf(14, 1):uint()

			if inner_t == 5 then
				t:add(zoom_o.fields.field, buf(14, 2))
				t:add(zoom_o.fields.payload, buf(16, 64))
			elseif inner_t == 2 then
				t:add(zoom_o.fields.field, buf(14, 2))
				t:add(zoom_o.fields.field, buf(16, 4))
				t:add(zoom_o.fields.field, buf(20, 4))
				local inner_inner_t = buf(24, 1):uint()
				if inner_inner_t == 5 then
					t:add(zoom_o.fields.field, buf(24, 2))
					t:add(zoom_o.fields.payload, buf(26, 64))
				else
					Dissector.get("data"):call(buf(24):tvb(), pkt, tree)
				end
			else
				Dissector.get("data"):call(buf(14):tvb(), pkt, tree)
			end
        end
	elseif outer_type == 4 then
		t:add(zoom_o.fields.control_type, buf(1, 2))
		t:add(zoom_o.fields.seq, buf(3, 2))
		t:add(zoom_o.fields.ts, buf(5, 4))
		t:add(zoom_o.fields.room, buf(9, 2))
		t:add(zoom_o.fields.id, buf(11, 2))
        t:add(zoom_o.fields.cont, buf(13, 1))
		local cont = buf(13, 1):uint()
		if cont == 1 then
			 local inner_t = buf(14, 1):uint()
            if inner_t == 5 then
                t:add(zoom_o.fields.field, buf(14, 2))
                t:add(zoom_o.fields.payload, buf(16, 64))
            else
				t:add(zoom_o.fields.field, buf(14, 2))
				t:add(zoom_o.fields.field, buf(16, 4))
				t:add(zoom_o.fields.field, buf(20, 10))
				t:add(zoom_o.fields.field, buf(30, 4))
				t:add(zoom_o.fields.field, buf(34, 4))
				t:add(zoom_o.fields.field, buf(38, 4))
                t:add(zoom_o.fields.field, buf(42, 2))
                t:add(zoom_o.fields.payload, buf(44, 64))
            end
		end
	elseif outer_type == 7 then
        t:add(zoom_o.fields.seq, buf(3, 2))
        t:add(zoom_o.fields.room, buf(5, 2))
        t:add(zoom_o.fields.id, buf(7, 2))
        t:add(zoom_o.fields.cont, buf(9, 1))
        local cont = buf(9, 1):uint()
        if cont == 1 then
            Dissector.get("data"):call(buf(10):tvb(), pkt, tree)
        end
    elseif outer_type == 5 then
		t:add(zoom_o.fields.seq, buf(1, 2))
        t:add(zoom_o.fields.room, buf(3, 2))
        t:add(zoom_o.fields.id, buf(5, 2))
	    t:add(zoom_o.fields.dir, buf(7, 1)):append_text(" (" .. get_zoom_o_dir_desc(buf(7, 1):uint()) .. ")")
        Dissector.get("zoom"):call(buf(8):tvb(), pkt, tree)
    else
        Dissector.get("data"):call(buf(9):tvb(), pkt, tree)
    end
end

-- per-default dissect all UDP port 8801 as Zoom Server Encap.
DissectorTable.get("udp.port"):add(8801, zoom_o)

-- allow selecting Zoom from "Decode as ..." context menu (for P2P traffic):
DissectorTable.get("udp.port"):add_for_decode_as(zoom)
