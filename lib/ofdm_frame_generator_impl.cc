/* -*- c++ -*- */
/*
 * Copyright 2022 gr-mimo_ofdm_jrc author.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "ofdm_frame_generator_impl.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    ofdm_frame_generator::sptr
    ofdm_frame_generator::make(int fft_len,
                                const std::vector<std::vector<int>>& occupied_carriers,
                                const std::vector<std::vector<int>>& pilot_carriers,
                                const std::vector<std::vector<gr_complex>>& pilot_symbols,
                                const std::vector<std::vector<gr_complex>>& sync_words,
                                int ltf_len,
                                const std::string& len_tag_key,
                                const bool output_is_shifted)
    {
        return gnuradio::get_initial_sptr
            (new ofdm_frame_generator_impl(fft_len,
                                            occupied_carriers,
                                            pilot_carriers,
                                            pilot_symbols,
                                            sync_words,
                                            ltf_len,
                                            len_tag_key,
                                            output_is_shifted));
    }


    /*
     * The private constructor
     */
    ofdm_frame_generator_impl::ofdm_frame_generator_impl(int fft_len,
                                                        const std::vector<std::vector<int>>& occupied_carriers,
                                                        const std::vector<std::vector<int>>& pilot_carriers,
                                                        const std::vector<std::vector<gr_complex>>& pilot_symbols,
                                                        const std::vector<std::vector<gr_complex>>& sync_words,
                                                        int ltf_len,
                                                        const std::string& len_tag_key,
                                                        const bool output_is_shifted)
      : gr::tagged_stream_block("ofdm_frame_generator",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex) * fft_len),
              len_tag_key),
        d_fft_len(fft_len),
        d_occupied_carriers(occupied_carriers),
        d_pilot_carriers(pilot_carriers),
        d_pilot_symbols(pilot_symbols),
        d_sync_words(sync_words),
        d_ltf_len(ltf_len),
        d_symbols_per_set(0),
        d_output_is_shifted(output_is_shifted)
    {
        // Sanity checks
        // If that is is null, the input is wrong -> force user to use ((),) in python
        if (d_occupied_carriers.empty()) {
            throw std::invalid_argument(
                "Occupied carriers must be of type vector of vector i.e. ((),).");
        }
        for (unsigned i = 0; i < d_occupied_carriers.size(); i++) {
            for (unsigned j = 0; j < d_occupied_carriers[i].size(); j++) {
                if (occupied_carriers[i][j] < 0) {
                    d_occupied_carriers[i][j] += d_fft_len;
                }
                if (d_occupied_carriers[i][j] > d_fft_len || d_occupied_carriers[i][j] < 0) {
                    throw std::invalid_argument("data carrier index out of bounds");
                }
                if (d_output_is_shifted) {
                    d_occupied_carriers[i][j] =
                        (d_occupied_carriers[i][j] + fft_len / 2) % fft_len;
                }
            }
        }
        if (d_pilot_carriers.empty()) {
            throw std::invalid_argument(
                "Pilot carriers must be of type vector of vector i.e. ((),).");
        }
        for (unsigned i = 0; i < d_pilot_carriers.size(); i++) {
            for (unsigned j = 0; j < d_pilot_carriers[i].size(); j++) {
                if (d_pilot_carriers[i][j] < 0) {
                    d_pilot_carriers[i][j] += d_fft_len;
                }
                if (d_pilot_carriers[i][j] > d_fft_len || d_pilot_carriers[i][j] < 0) {
                    throw std::invalid_argument("pilot carrier index out of bounds");
                }
                if (d_output_is_shifted) {
                    d_pilot_carriers[i][j] = (d_pilot_carriers[i][j] + fft_len / 2) % fft_len;
                }
            }
        }
        if (d_pilot_symbols.empty()) {
            throw std::invalid_argument(
                "Pilot symbols must be of type vector of vector i.e. ((),).");
        }
        for (unsigned i = 0; i < std::max(d_pilot_carriers.size(), d_pilot_symbols.size());
            i++) {
            if (d_pilot_carriers[i % d_pilot_carriers.size()].size() !=
                d_pilot_symbols[i % d_pilot_symbols.size()].size()) {
                throw std::invalid_argument("pilot_carriers do not match pilot_symbols");
            }
        }
        for (unsigned i = 0; i < d_sync_words.size(); i++) {
            if (d_sync_words[i].size() != (unsigned)d_fft_len) {
                throw std::invalid_argument("sync words must be fft length");
            }
        }

        for (unsigned i = 0; i < d_occupied_carriers.size(); i++) {
            d_symbols_per_set += d_occupied_carriers[i].size();
        }
        set_tag_propagation_policy(TPP_DONT);
        set_relative_rate((uint64_t)d_symbols_per_set, (uint64_t)d_occupied_carriers.size());
    }

    /*
     * Our virtual destructor.
     */
    ofdm_frame_generator_impl::~ofdm_frame_generator_impl()
    {
    }

    int
    ofdm_frame_generator_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
        int nin = ninput_items[0];
        int nout = (nin / d_symbols_per_set) * d_occupied_carriers.size();
        int k = 0;
        for (int i = 0; i < nin % d_symbols_per_set; k++) {
            nout++;
            i += d_occupied_carriers[k % d_occupied_carriers.size()].size();
        }
        return nout + d_sync_words.size();
    }

    int
    ofdm_frame_generator_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const gr_complex* in = (const gr_complex*)input_items[0];
        gr_complex* out = (gr_complex*)output_items[0];
        std::vector<tag_t> tags;

        memset((void*)out, 0x00, sizeof(gr_complex) * d_fft_len * noutput_items);
        // Copy Sync word
        for (unsigned i = 0; i < d_sync_words.size(); i++) {
            memcpy((void*)out, (void*)&d_sync_words[i][0], sizeof(gr_complex) * d_fft_len);
            out += d_fft_len;
        }

        // Copy data symbols
        long n_ofdm_symbols = 0; // Number of output items
        int curr_set = 0;
        int symbols_to_allocate = d_occupied_carriers[0].size();
        int symbols_allocated = 0;
        for (int i = 0; i < ninput_items[0]; i++) {
            if (symbols_allocated == 0) {
                // Copy all tags associated with these input symbols onto this OFDM symbol
                get_tags_in_range(
                    tags,
                    0,
                    nitems_read(0) + i,
                    nitems_read(0) + std::min(i + symbols_to_allocate, (int)ninput_items[0]));
                for (unsigned t = 0; t < tags.size(); t++) {
                    add_item_tag(0,
                                nitems_written(0) + n_ofdm_symbols +
                                    (n_ofdm_symbols == 0 ? 0 : d_sync_words.size()),
                                tags[t].key,
                                tags[t].value);
                }
                n_ofdm_symbols++;
            }
            out[(n_ofdm_symbols - 1) * d_fft_len +
                d_occupied_carriers[curr_set][symbols_allocated]] = in[i];
            symbols_allocated++;
            if (symbols_allocated == symbols_to_allocate) {
                curr_set = (curr_set + 1) % d_occupied_carriers.size();
                symbols_to_allocate = d_occupied_carriers[curr_set].size();
                symbols_allocated = 0;
            }
        }
        // Copy pilot symbols
        for (int i = 0; i < n_ofdm_symbols; i++) {
            for (unsigned k = 0; k < d_pilot_carriers[i % d_pilot_carriers.size()].size();
                k++) {
                out[i * d_fft_len + d_pilot_carriers[i % d_pilot_carriers.size()][k]] =
                    d_pilot_symbols[i % d_pilot_symbols.size()][k];
            }
        }

        return n_ofdm_symbols + d_sync_words.size();
    }

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

